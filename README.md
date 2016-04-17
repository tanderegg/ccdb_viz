# CCDB Visualization Tool

## Summary

This project is a tool for visualizing the CFPB's public Consumer Complaint dataset as compared to the median income of the zip code the complaint comes from.  For general reference, the top of the page has a bar graph displaying the number of complaints that come from each state.  Below that is a scatter plot of the number of complaints and the median income for each zip code.  For ease of use and readability, the application limits the number of data points to 5000.  The complaints vs income graph can be interactively modified useing the filters on the left, such as state, the product being complained about, and the issues consumers faced.

## Instructions

The application can be viewed directly in a browser by opening the "main.html" file located in the html folder.  However, the web application will not be fully interactive without a live Bokeh server and PostgreSQL connection, as the data is dynamically retrieved from the database when the user interacts with the UI.

If you'd rather recreate the application from source, and experience the fully interactive version of the application, please follow these instructions:

1. Make sure you are on a POSIX compliant system such as Linux or Mac OSX
1. Check to see if you have [Vagrant](http://www.vagrantup.com) and [Ansible](http://www.ansible.com) installed.  If you have pip available, the build process will install Ansible for you if it is not already installed, but Vagrant must be installed via your system package manager.
1. After cloning this repository, change your directory to the ccdb_viz folder, and run `make`
1. Make will provision a virtual machine with PostgreSQL and some python utilities, then download, extract, transform, and load the required datasets.  Lastly, it will deploy and execute the ccdb_viz application.
1. The application will be viewable at http://10.0.1.2:5006/main on your host machine once Make has finished.
