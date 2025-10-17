## **TA ONLY**

The files here are for TA use only. Do not upload to the main repo.

***

### **Instructions to use:**

- The notebook file `gen_data.ipynb` contains the Python code for generating the dataset.

- The datasets that were used in the procedure are listed below:

    - Drinking water accessibility data: ["Drinking water, sanitation and hygiene in households by country, 2000-2020"](https://data.unicef.org/topic/water-and-sanitation/drinking-water/)  drawn from Unicef / WHO joint report on water supply, sanitation, and hygiene (2021)
    - World Bank income level data: historical classification by income from the webpage ["The World by Income and Region"](https://datatopics.worldbank.org/world-development-indicators/the-world-by-income-and-region.html)
    - World Bank region data: ["World Bank Country and Lending Groups"](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups)


- The steps taken to yield the final dataset are as follows:
    - Remove rows in which the specific country does not have data for both years 2015 / 2020, and only choose the relevant columns from drinking water accessibility data (this step was done through Microsoft Excel)
    - Merge drinking water accessibility data with income level data
    - Merge the previously generated data with region data
    - Transform the format of original income level, from single initial to descriptive phrases (e.g., 'Lower middle income')
