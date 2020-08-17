# LyftDataAnalysis

## Overview
Given drivers information, rides information, and drivers-rides pairs, we analyzed the lifetime value of a driver, namely, the projected value of a driver over the entire projected lifetime. By data analysis and machine learning, we analyzed the main factors that affect a driver's lifetime value, predicted the average lifetime of a driver, performed analysis of drivers in various group, and gave business suggestions based on the results.

## Techniques/Packages we used
Numpy, Pandas, Python, JupyterNotebook, Exploratory Data Analysis, Seaborn, Linear Regression, Ordinary Least-Squared model, scikit-learn, etc.

## Conclusion
We realized that night-time drivers generate more profits because they tend to accept rides continuously whenever they see a request. Since they were dedicated on driving throughout the night, they adhered to their schedule in a high efficiency. In order to optimize profits that are generated, we would like to give out the following recommendations:

1. Based on the night rides demand of the location, we would like to recommend a policy that increases drivers' incentives of extending the time driving at night time or the adherent period driving at day time. Prior to the making of policy, we recommend designing an algorithms to classify drivers into night-time drivers and day-time drivers. Since the average daily driving time for each driver is 1.5 hours with a standard deviation of 0.67 hours, and the 75 percentile ride distance completed is at 8.095 kilometers, we propose to give night-time drivers bonus if they continuously drive for 4 hours between 9PM to 6AM, OR if completed 161.900 kilometers daily for five consecutive days between 6AM to 9PM. 

2. Considering current drivers who generate different levels of Lifetime value to Lyft, we recommend designing a new algorithm for distributing customer requests to effectively increase each driver's lifetime value. Based on the analysis, low-value drivers should drive longer distance to obtain higher value, while medium-value drivers should drive more efficiently to increase their value, such as increasing their ride speed in a fixed ride distance (under secure circumstances). And high-value drivers should try to increase their profit per ride, such as accepting more prime time tickets. In other words, the algorithm could distribute more ride requests which contains less uncertainties like traffics to current low-value drivers, assign more rides with potential profit such as the ones during prime time to more experienced drivers, i.e. high-value drivers, and let other medium-value drivers accept most of the rest requests.
