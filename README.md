# Colorifix Technical Summary
I believe I was able to complete the task roughly within the time limit. I was enjoying the task so built out a little bit beyond the time limit.
# Installation
In order to use this API to edit the neo4J database, and because the project is containerised you will need to:
  1. Ensure Docker Desktop is installed and running: (you can download here: [Get Docker Download](https://www.docker.com/get-started/)
  2. Ensure that you have a copy of neo4j desktop installed: (you can download here: [Get neo4j Desktop Download](https://neo4j.com/cloud/platform/aura-graph-database/?ref=nav-get-started-cta)
  3. Create a database and start it running, use the below credentials:
        ```python
        URI = "bolt://localhost:7687"
        USER = "neo4j"
        PASSWORD = "password"
        ```
  4. Ensure that your project folder is labelled 'colorixfix_technical'
  4. clone the repository to your local machine.
  5. Using the docker-compose.yml you should be able to right click and compose up if you are using VSCode or use the command line.
  6. ``` localhost:8000/docs``` to access the API interface
  7. ``` http://localhost:7474/browser/``` to access the neo4J database.
  8. Requirements are all contained in the requirements.txt file.
     
# Technologies Used
## neo4J
This is a new technology to me and seeing that it is used extensively at Colorifix I wanted to learn to use it for this task.
## FASTAPI
I used FastAPI as I knew it was similar to Starlite and the Starlite link was broken for me.
## Docker
I used Docker to containerise the project and make it easier to get up and running.

Due to time constraints, I did not use poetry but I have heard good things for my next project I may well take the plunge.

# TODO
There are plenty of ways to improve my project so below are a few ideas:
1. Split up the python module into a data module and a FASTAPI module
2. Implement API tests
3. Reformat/optimize - Priority was to get working first and then optimize afterwards
4. Include more exception handling
5. Extend the data model to take the table as an input

# Data
I chose to sanitise the data in the data model, a nice extension would be to take the table and feed that into the data model to increase the extensibility of the project. Also, I chose to create the permissions as nodes attached to the permission group so that they could be shared or removed from other permission groups, as a pose to properties attached to permission groups.

# Final Thoughts
I really enjoyed working with these new technologies, I hope the project is satisfactory and if you have any questions or I have missed anything please do get in touch.
