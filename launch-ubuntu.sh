#!/bin/bash


########
# This script ASSUMES Ubuntu to know if the correct packages are installed.
# Please update the script accordingly for your own distribution.
#######

input=$1 # input file if not the normal one.
auto_simc_pwd=$(pwd) # current directory to get back to later.


if [[ -z $input ]]; then
	input=$auto_simc_pwd/input.txt # use the defualt input file if none specified.
fi

prompt=""
while [[ $prompt != Y ]]; do 
	# Ask the user if they want to download SIMC. TODO: check if we're already on the newest version...
	echo "Do you want to fully download and build simc? (Y/N) WARNING: This may take a very long time."
	read prompt 
	prompt=$(echo $prompt | tr [a-z] [A-Z]) # upcase
	if [[ $prompt == "Y" ]]; then
		
		if [[ -z $(dpkg -l | grep build-essential) ]]; then
			# check if build-essential is installed, if not install it
			echo "Installing build-essential"
			sudo apt-get install -y build-essential
		fi
		echo "build-essential is installed"

		if [[ -z $(dpkg -l | grep libssl-dev) ]]; then
			# check if libssl-dev is installed, if not install it
			echo "Installing libssl-dev"
			sudo apt-get install -y libssl-dev
		fi
		echo "libssl-dev is installed"

		# HERE: check version that we have and determine if we really need to update.
		echo "Installing Simc to ~/simc.."
		mkdir -p ~/simc	# create a simc folder in the home dir
		cd ~/simc
		rm -r * #remove everything if there is anything.
		echo "Downloading the source code.."
		wget $(curl --silent "http://www.simulationcraft.org/download.html" | grep -ioP \".*github.*archive.*\" | tr -d \") # download the source code
		echo "Extracting the source code.."
		unzip *.zip
		rm *.zip
		cd simc*/engine
		echo "Compiling simc"
		make OPENSSL=1 optimized # build from source
		
		echo "Setting your simc executable in your settings_local.py"
		simc_location="r'$(pwd)/simc'" # get the executable location
		sed "s~simc_path = .*~simc_path = $simc_location~g" $auto_simc_pwd/settings.py > temp # update the settings file with the executable path.
	    mv temp $auto_simc_pwd/settings_local.py # use a local settings file so we don't have to overwrite the original.

	elif [[ $prompt == "N" ]]; then
		break
	fi
done

echo "Running AutoSimC"

cd $auto_simc_pwd

# UPDATE THIS PYTHON BASED ON YOUR PATH
python3 main.py -i $input -o out.simc -sim all
