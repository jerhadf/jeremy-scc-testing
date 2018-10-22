# PyLAT
The Legrand automated testing framework for running interactive tests.

[TOC]



## Installing

Using Pip (Currently not supported)

1. ~~Add the file `~/.pip/pip.conf` to your filesystem if it doesn't already exist.~~

2. ~~Add the following contents to the `pip.conf` file.~~
    ```
    [global]
    extra-index-url = https://finalpypiurl.com/pypi
    ```

3. ~~From the command line run `$ pip install pylat`~~

Building from Source

1. Clone this repository.
2. cd into pylat.
3. run `python setup.py build`
4. run `python setup.py install`

## Using In a Project
PyLAT simplifies the running of tests by using definitions stored in a config file. 

A sample project might look like the following.
```
/myproduct
    /tests
        __init__.py
        testA.py
        testB.py
        testC.py
        ...
    /config
        configOne.json
        configTwo.json
        ...
```

To run the tests simply use the following command in the myproduct folder
```commandline
$ python -m pylat -c config/configOne.json
```
## Asking Questions Using PyLAT

One of the main features of PyLAT is its ability to automate 'interactive' tests by querying the user locally (through the command line).

To ask a question, use the `ask_question` function from PyLAT.

**ask_question**(_question_, _answers_, _img=None_)

*question*: The question to ask. The length of the question should be less than 200 characters. 

*answers*: The list of answers presented to the user.

`ask_question` returns the user selected answer from those provided.

## Writing a Test Using PyLAT

PyLAT tests must be written in the unittest format. More information about the `unittest` module can be found [here](https://docs.python.org/3/library/unittest.html).

The following is a sample test that uses PyLAT's interactive features.

```python
import unittest
from pylat.query import ask_question
    
class TestSomething(unittest.TestCase):
    
    def test_lightFlash(self):
      	...
        # user code to make light flash.
        ...
        
        response = ask_question("Is the light flashing?", ["Yes", "No"])
        self.assertEqual(response, "Yes")
```
## Writing a Config File
The config file determines the basic behavior of PyLAT. A config file is written in json format and contains the following types of values.
#### Required
**tests** : The list of tests to run. The tests will be run in the order they appear in the list.

#### Optional
Besides the required values, you can provide any number of user defined values.
These values can be accessed inside the tests you write using the `get_config` function.

For example if you needed to connect to a hardware device during testing and needed the device id,
you could include a **device_id** value in the config file and access it inside the appropriate tests.

```python
import unittest
from pylat import ask_question
from pylat import get_config
    
class TestDeviceConnection(unittest.TestCase):
    
    def test_canConnect(self):
        ...
        device_id = get_config("device_id")
        ...
```
#### Sample Config File
```json
{
  "tests" : ["tests.testA", "tests.testB"],
  
  "device_id" : "a0:12:55:01:fe"
}
```
