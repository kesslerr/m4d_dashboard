
# in the conda env

conda list --export > requirements.txt

conda list --export | grep -v '^#' | cut -d '=' -f 1,2 > requirements.txt

# replace all = with == in requirements.txt content

sed -i 's/=//g' requirements.txt