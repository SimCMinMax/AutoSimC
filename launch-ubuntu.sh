#!/bin/bash


########
# This script ASSUMES Ubuntu to know if the correct packages are installed.
# Please update the script accordingly for your own distribution.
#######

echo "NOTE: Running this script for the first time is recommended as sudo/root incase any simc dependencies are missing."
echo "NOTE: If you already have the dependencies (build-essential libssl-dev) installed, you do not need root."

input=$1 # input file if not the normal one.
auto_simc_pwd=$(pwd) # current directory to get back to later.

if [[ -z $input ]]; then
  input=$auto_simc_pwd/input.txt # use the defualt input file if none specified.
fi

check_dependency() {
  p=""
  for dep in build-essential libssl-dev; do
    echo "Checking if ${dep} is installed.."
    if [[ -z $(dpkg -l | grep ${dep}) ]]; then
      # check if dep is installed, if not install it
      while [[ $p != Y ]]; do
        echo "${dep} is not installed Do you want to install it? (Y/N) (requires root)"
        read p
        p=$(echo $p | tr [a-z] [A-Z]) # upcase

        case $p in
          Y)
            sudo apt-get install -y ${dep}
            ;;
          N)
            echo "${dep} installation canceled. Aborting script."
            exit 1
            ;;
        esac
      done
    fi
	echo "${dep} is installed"
  done
}

download_and_compile_simc_zip() {
  echo "Downloading Simc source code to ~/simc.."
  mkdir -p ~/simc	# create a simc folder in the home dir
  cd ~/simc
  rm -r * #remove everything if there is anything.

  default_branch=$(curl -s https://api.github.com/repos/simulationcraft/simc | sed -n 's/.*"default_branch": "\(.*\)",/\1/p') # could force 'jq' to be installed, but rather not do that to people.
  wget https://github.com/simulationcraft/simc/zipball/${default_branch}

  #compile
  echo "Extracting the source code.."
  unzip $default_branch
  rm $default_branch

  echo "Compiling simc"
  cd *simc*/engine
  make OPENSSL=1 optimized # build from source

  # set the new path in the setting file.
  echo "Setting your simc executable in your settings_local.py"
  simc_location="r'$(pwd)/simc'" # get the executable location
  sed "s~simc_path = .*~simc_path = $simc_location~g" $auto_simc_pwd/settings.py > temp # update the settings file with the executable path.
  mv temp $auto_simc_pwd/settings_local.py # use a local settings file so we don't have to overwrite the original.
}

check_dependency_fedora() {
	for dep in openssl-devel autoconf automake binutils bison flex gcc gcc-c++ gdb glibc-devel libtool make pkgconfig strace; do
		rpm -q ${dep} > /dev/null
		echo Checking Dependency ${dep}
		if [ $? -ne 0 ] ; then
			yum install -y ${dep}
		fi
	done
}

prompt() {
  prompt=""
  while [[ $prompt != Y ]]; do
    # Ask the user if they want to download SIMC. TODO: check if we're already on the newest version...
    echo "Do you want to fully download and build simc? (Y/N) WARNING: This may take a very long time."
    read prompt
    prompt=$(echo $prompt | tr [a-z] [A-Z]) # upcase

    case $prompt in
      Y)
		cat /etc/redhat-release | grep Fedora > /dev/null
		if [ $? -eq 0 ] ; then
			check_dependency_fedora
		else
			check_dependency
		fi
        download_and_compile_simc_zip
        ;;
      N)
        break
        ;;
    esac

  done
}

run_auto_simc() {
  echo "Running AutoSimC"
  cd $auto_simc_pwd

  # UPDATE THIS PYTHON BASED ON YOUR PATH
  python3 main.py -i $input -o out.simc -sim all
  # gave up trying to 'auto find python exe'.  Not worth the for loop when the user can just change 1 line.
}

# prompt for installation.
prompt
# run auto simc
run_auto_simc
