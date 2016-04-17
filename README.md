# CCDB Visualization Tool

## Summary

This project is a tool for visualizing the CFPB's public Consumer Complaint dataset as compared to the median income of the zip code the complaint comes from.  For general reference, the top of the page has a bar graph displaying the number of complaints that come from each state.  Below that is a scatter plot of the number of complaints and the median income for each zip code.  For ease of use and readability, the application limits the number of data points to 5000 via sampling.  The complaints vs income graph can be interactively modified using the filters on the left of the page, such as state, the product being complained about, and the issues consumers faced.

This tool can be used to notice some interesting patterns.  For example, in general there are many more zip codes with a high number of complaints in the middle to middle-low range of median income (approx 20K to 60K per year), while there are almost none below 20K or above 80K.  There are of course many more zip codes within the 20K-60K range in general, but the pattern is evident nonetheless.  Likely this is because low income communities simply have many fewer interactions with financial services, while higher income communities generally hire others to deal with their finances, and likely receive more attentive treatment when they do interact with financial institutions.

The pattern shifts depending on the financial product in question however.  Notable mortgage products have a much wider spread in terms of numbers of complaints compared to median income, likely due to the complexity of mortgages and the fact that upper income communities generally have a higher ownership rate than lower income communities to begin with.

## Instructions

The application can be viewed directly in a browser by opening the "main.html" file located in the html folder.  However, the web application will not be fully interactive without a live Bokeh server and PostgreSQL connection, as the data is dynamically retrieved from the database when the user interacts with the UI.

If you'd rather recreate the application from source, and experience the fully interactive version of the application, please follow these instructions. Note that it takes approximately 20 minutes to complete the full VM provisioning, ETL of the datasets, and deployment of the application.

1. Make sure you are on a POSIX compliant system such as Linux or Mac OSX
1. Check to see if you have [Vagrant](http://www.vagrantup.com) and [Ansible](http://www.ansible.com) installed.  If you have pip available, the build process will install Ansible for you if it is not already installed, but Vagrant must be installed via your system package manager.
1. After cloning this repository, change your directory to the ccdb_viz folder, and run `make`.
1. Make will provision a virtual machine with PostgreSQL and some python utilities, then download, extract, transform, and load the required datasets. Lastly, it will deploy and execute the ccdb_viz application. Please be patient, as installing Pandas and Numpy can take some time.
1. The application will be viewable at http://192.168.56.1:5006/main on your host machine once Make has finished.

## Implementation Notes and Troubleshooting

- If you receive an "Error: unreachable" message from your browser, it is possible that the VM's IP address is conflicting with another IP address on your host machine or network.  Edit the ip address in the Vagrantfile, and run `vagrant reload` to try a different IP address.  You will also need to modify the --host parameter passed to Bokeh in the Makefile, before running `make run` to test out the application.

- Bokeh is still in its early stages of development, and while it has a lot of potential as Python's answer to R Shiny, it is not there yet.  It is difficult to add custom content such as text boxes or images without wrapping the entire Bokeh application in a Flask application, which is quite complex, and it's API is not yet standardized, making it difficult to work with different types of charts and graphs in a consistent manner.  For example, the bar graph at the top is generated using the Bar helper model, but it does not allow the easy dynamic updating that the scatter plot does, which was built using lower level primitives.  Bokeh does seem to be evolving rapidly, however, so it's worth keeping an eye on it.
