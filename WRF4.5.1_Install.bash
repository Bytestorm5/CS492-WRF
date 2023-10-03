#!/bin/bash
#########################################################
#		WRF Install Script     			#
# 	This Script was written by Umur Dinç    	# Modified by Ansel Obergfell for capstone
#  To execute this script "bash WRF4.5.1_Install.bash"	#
#########################################################
WRFversion="4.5.1"
type="ARW"
echo "Welcome! This Script will install the WRF${WRFversion}-${type}"
echo "Installation may take several hours and it takes 52 GB storage. Be sure that you have enough time and storage."
#########################################################
#	Controls					#
#########################################################
if [ "$EUID" -eq 0 ]
  then echo "Running this script as root or sudo, is not suggested"
  exit
fi
osbit=$(uname -m)
if [ "$osbit" = "x86_64" ]; then
        echo "64 bit operating system is used"
else
        echo "Sorry! This script was written for 64 bit operating systems."
exit
fi
########
packagemanagement=$(which apt)
if [ -n "$packagemanagement" ]; then
        echo "Operating system uses apt packagemanagement"
else
        echo "Sorry! This script is written for the operating systems which uses apt packagemanagement. Please try this script with debian based operating systems, such as, Ubuntu, Linux Mint, Debian, Pardus etc."
#Tested on Ubuntu 20.04
exit
fi
local_language=$(locale | grep LANG | grep tr_TR)
if [ -n "$local_language" ]; then
 echo "Merhaba, WRF modelinin kodundaki hatadan dolayı, WRF kurulumu işletim sistemi dili Türkçe olduğunda, Türkçedeki i ve ı harflerinin farklı olması sebebiyle hata vermektedir. Lütfen işletim sisteminizin dilini başka bir dile çevirip yeniden çalıştırınız. Kurulum bittikten sonra işletim sistemi dilini tekrar Türkçe'ye çevirebilirsiniz."
 exit
fi
#########################################################
#   Installing neccesary packages                       #
#########################################################

echo "Please enter your sudo password, so necessary packages can be installed."
sudo hwclock --hctosys
sudo apt-get update
mpich_repoversion=$(apt-cache policy mpich | grep Candidate | cut -d ':' -f 2 | cut -d '-' -f 1 | cut -c2)
if [ "$mpich_repoversion" -ge 4 ]; then
mpirun_packages="libopenmpi-dev libhdf5-openmpi-dev"
else
mpirun_packages="mpich libhdf5-mpich-dev"
fi
sudo apt-get install -y build-essential csh gfortran m4 curl perl ${mpirun_packages} libpng-dev netcdf-bin libnetcdff-dev ${extra_packages}

package4checks="build-essential csh gfortran m4 curl perl ${mpirun_packages} libpng-dev netcdf-bin libnetcdff-dev ${extra_packages}"
for packagecheck in ${package4checks}; do
 packagechecked=$(dpkg-query --show --showformat='${db:Status-Status}\n' $packagecheck | grep not-installed)
 if [ "$packagechecked" = "not-installed" ]; then
        echo $packagecheck "$packagechecked"
     packagesnotinstalled=yes
 fi
done
if [ "$packagesnotinstalled" = "yes" ]; then
        echo "Some packages were not installed, please re-run the script and enter your root password, when it is requested."
exit
fi
#########################################
cd ~
mkdir Build_WRF
cd Build_WRF
mkdir LIBRARIES
cd LIBRARIES
echo "" >> ~/.bashrc
bashrc_exports=("#WRF Variables" "export DIR=$(pwd)" "export CC=gcc" "export CXX=g++" "export FC=gfortran" "export FCFLAGS=-m64" "export F77=gfortran" "export FFLAGS=-m64"
		"export NETCDF=/usr" "export HDF5=/usr/lib/x86_64-linux-gnu/hdf5/serial" "export LDFLAGS="\""-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -L/usr/lib"\""" 
		"export CPPFLAGS="\""-I/usr/include/hdf5/serial/ -I/usr/include"\""" "export LD_LIBRARY_PATH=/usr/lib")
for bashrc_export in "${bashrc_exports[@]}" ; do
[[ -z $(grep "${bashrc_export}" ~/.bashrc) ]] && echo "${bashrc_export}" >> ~/.bashrc
done
DIR=$(pwd)
export CC=gcc
export CXX=g++
export FC=gfortran
export FCFLAGS=-m64
export F77=gfortran
export FFLAGS=-m64
export NETCDF=/usr
export HDF5=/usr/lib/x86_64-linux-gnu/hdf5/serial
export LDFLAGS="-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -L/usr/lib"
export CPPFLAGS="-I/usr/include/hdf5/serial/ -I/usr/include"
export LD_LIBRARY_PATH=/usr/lib
##########################################
#	Jasper Installation		#
#########################################
[ -d "jasper-1.900.1" ] && mv jasper-1.900.1 jasper-1.900.1-old
[ -f "jasper-1.900.1.tar.gz" ] && mv jasper-1.900.1.tar.gz jasper-1.900.1.tar.gz-old
wget https://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/jasper-1.900.1.tar.gz -O jasper-1.900.1.tar.gz
tar -zxvf jasper-1.900.1.tar.gz
cd jasper-1.900.1/
./configure --prefix=$DIR/grib2
make
make install
[[ -z $(grep "export JASPERLIB=$DIR/grib2/lib" ~/.bashrc) ]] && echo "export JASPERLIB=$DIR/grib2/lib" >> ~/.bashrc
[[ -z $(grep "export JASPERINC=$DIR/grib2/include" ~/.bashrc) ]] && echo "export JASPERINC=$DIR/grib2/include" >> ~/.bashrc
export JASPERLIB=$DIR/grib2/lib
export JASPERINC=$DIR/grib2/include
cd ..
#########################################
#	WRF Installation		#
#########################################
cd ..
[ -d "WRFV${WRFversion}" ] && mv WRFV${WRFversion} WRFV${WRFversion}-old
[ -f "WRFV${WRFversion}.tar.gz" ] && mv WRFV${WRFversion}.tar.gz WRFV${WRFversion}.tar.gz-old
wget https://github.com/wrf-model/WRF/releases/download/v${WRFversion}/v${WRFversion}.tar.gz -O WRFV${WRFversion}.tar.gz
tar -zxvf WRFV${WRFversion}.tar.gz
cd WRFV${WRFversion}
sed -i 's#$NETCDF/lib#$NETCDF/lib/x86_64-linux-gnu#g' configure
( echo 34 ; echo 1 ) | ./configure
sed -i 's#-L/usr/lib -lnetcdff -lnetcdf#-L/usr/lib/x86_64-linux-gnu -lnetcdff -lnetcdf#g' configure.wrf
gfortversion=$(gfortran -dumpversion | cut -c1)
if [ "$gfortversion" -lt 8 ] && [ "$gfortversion" -ge 6 ]; then
sed -i '/-DBUILD_RRTMG_FAST=1/d' configure.wrf
fi
logsave compile.log ./compile em_real
if [ -n "$(grep "Problems building executables, look for errors in the build log" compile.log)" ]; then
        echo "Sorry, There were some errors while installing WRF."
        echo "Please create new issue for the problem, https://github.com/bakamotokatas/WRF-Install-Script/issues"
        exit
fi
cd ..
[ -d "WRF-${WRFversion}-${type}" ] && mv WRF-${WRFversion}-${type} WRF-${WRFversion}-${type}-old
mv WRFV${WRFversion} WRF
#########################################
#	WPS Installation		#
#########################################
WPSversion="4.5"
[ -d "WPS-${WPSversion}" ] && mv WPS-${WPSversion} WPS-${WPSversion}-old
[ -f "WPSV${WPSversion}.TAR.gz" ] && mv WPSV${WPSversion}.TAR.gz WPSV${WPSversion}.TAR.gz-old
wget https://github.com/wrf-model/WPS/archive/v${WPSversion}.tar.gz -O WPSV${WPSversion}.TAR.gz
tar -zxvf WPSV${WPSversion}.TAR.gz
cd WPS-${WPSversion}
./clean
sed -i '163s/.*/    NETCDFF="-lnetcdff"/' configure
sed -i "s/standard_wrf_dirs=.*/standard_wrf_dirs=\"WRF-${WRFversion}-${type} WRF WRF-4.0.3 WRF-4.0.2 WRF-4.0.1 WRF-4.0 WRFV3\"/" configure
echo 3 | ./configure
logsave compile.log ./compile
sed -i "s# geog_data_path.*# geog_data_path = '../WPS_GEOG/'#" namelist.wps
cd ..
#########################################
#	Opening Geog Data Files 	#
#########################################
if [ -d "WPS_GEOG" ]; then
  echo "WRF and WPS are installed successfully"
  echo "Directory WPS_GEOG is already exists."
  echo "Do you want WPS_GEOG files to be redownloaded and reexracted?"
  echo "please type yes or no"
  read GEOG_validation
  if [ ${GEOG_validation} = "yes" ]; then
    wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_high_res_mandatory.tar.gz -O geog_high_res_mandatory.tar.gz
    tar -zxvf geog_high_res_mandatory.tar.gz
  else
    echo "You can download it later from http://www2.mmm.ucar.edu/wrf/src/wps_files/geog_high_res_mandatory.tar.gz and extract it"
   fi
else
wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_high_res_mandatory.tar.gz -O geog_high_res_mandatory.tar.gz
tar -zxvf geog_high_res_mandatory.tar.gz
fi
##########################################################
#       Ansel's additional calls                        #
##########################################################
mv WPS-${WPSversion} WPS
rm *.gz
cd ..
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=12YL3DNPQwIJyIP026onv3nRvZLQJuo9F' -O 'Data.tar.gz'
tar -zxvf Data.tar.gz 
rm *.gz
##########################################################
#      Running Geogrid                                  #
##########################################################
cd Build_WRF
export geogloc=`pwd`/WPS_GEOG/
cd WPS
rm namelist.wps
mv ~/Data/WPS_Input/namelist.wps `pwd`
sed -i "s~^ geog_data_path.*~geog_data_path = '${geogloc}',~" ./namelist.wps
ln -s geogrid/GEOGRID.TBL.ARW GEOGRID.TBL
./geogrid.exe
##########################################################
#      Running Ungrib                                   #
##########################################################
mv ~/Data/WPS_Input/Vtable `pwd`
./link_grib.csh ~/Data/WPS_Input/fnl*
./ungrib.exe
##########################################################
#      Running Metgrid                                  #
##########################################################
ln -s metgrid/METGRID.TBL.ARW METGRID.TBL
./metgrid.exe
##########################################################
#      Running WRF                                      #
##########################################################
cd ..
cd WRF/run
rm namelist.input
mv ~/Data/namelist.input `pwd`
ln -sf ~/Build_WRF/WPS/met_em* .
##########################################################
#	End						#
##########################################################
echo "Installation has completed"
echo "You can now run mpiexec -np <Number of proccessors reccomended=4> (./real.exe -> ./wrf.exe)"
exec bash
exit