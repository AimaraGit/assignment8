I made simple app that has 3 main functions: 1)create task, 2)list tasks, 3) delete task. 
In 2 python files i have app body and testings (12 tests). 
Also there are requirements that need to be downloaded in python for dependencies. 
Gitignore is for github to ignore unnecessary files. 
App log registers all testing informations from CICD pipeline tests.
In CICD there are 3 actions where by task firstly the requirements have some vulnerable libraries caught by pip audit. Then workflow isnt correct.
I change flask's version to not vulnerable one, and then workflow works fine.
Test's workflow works totally fine.
