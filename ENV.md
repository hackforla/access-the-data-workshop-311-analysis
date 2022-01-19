# Notes on the env

I use jupyter lab with folium, ipywidgets, ipyleaflet, bqplot, and qgrid. Here's a simple recipe to set it up from scratch.  

  1. Make sure Anaconda is installed and `git lfs clone` the repository from github.  cd into the data-literacy folder.  
  
  2. In the data-literacy folder you should see the environment.yml file.  Use this to build the env using conda:  `conda env create -f environment.yml`
  
  3. Once the create env is completed, activate the new env: `conda activate data-literacy`
  
  4. At this point you will have a working jupyter lab with the necessary widgets.  Launch the lab with `juptyer lab`.
  
  5. You're ready to explore, understand, develop, ...
  
