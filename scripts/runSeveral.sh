# Execute all simulations within a folder
search_dir=$1
for entry in "$search_dir"/*
do
  python3 billiards.py "$entry"
done