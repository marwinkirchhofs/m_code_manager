**MAIN BRANCH README CURRENTLY FROM LEGACY PROJECT, USE DEV BRANCH (AND WIKI)**

# Project Creator

## usage

```bash
create_project [options] <app_name>
```

#### global options
###### required
| option | action |
| --- | --- |
| ```-l <language>``` | specify the language (-> template to be loaded) |

###### optional
| option | action |
| --- | --- |
| ```--git``` | initialize a git repo |
| ```--vimspector``` | create a config (from the language-specific template) for the vimspector debugger |

#### language-specific options
###### python

| option | action |
| --- | --- |
| ```--py_pkg <package-name>``` | sets up a package within the project, creates the ```__init__.py``` and imports the package |

###### c/cpp

| option | action |
| --- | --- |
| ```--cuda ``` | add cuda support to ```CMakeLists.txt``` |

## adding a new template

Adding a new template requires a few steps and classes/functions to be 
implemented and integrated. The list below goes through all of these steps, 
where the existing options (e.g. for python) can be used as a blueprint.  
Actually, there is not that much changing and it might be possible to transform 
that into a convenient yaml-based flow so that one only has to add the template 
files and configure the parsing via yaml. But honestly don't know if it's worth 
the time and I also simply might not have the time :-D

###### TEMPLATES
  * new directory *templates/<new_language>*
  * within that, desired templates named *template_<file_type>*
    * templates are parameterized by the given template variables plus 
      additional variables to be defined on one's own
###### LANGUAGE-SPECIFIC PROJECT CREATOR CLASS
  * within *templates*, create a new file and class called 
    *<new_language>_Project_Creator.py*
  * inherit from *Project_Creator*
    * sets up **self.TEMPLATES_ABS_PATH**
    * provides non-language dependent functions such as **_load_template** and **_create_git**
  * implement ```create_project```
    * basically calls all separate file/whatever creation functions
    * all possible keyword arguments for this language (equivalent to option 
      parser fields) need to be explicit parameters for ```create_project```, an 
      additional **\*\*args** is helpful for effectively ignoring everything 
      else
  * implement the separate template parsing functions (boilerplate scheme is 
    given below -> TODO)
###### TEMPLATE PACKAGE LOADING
  * add the new class to the template package import script 
    (*templates/\__init__.py*)
    ```python
    from <new_language>_Project_Creator import <new_language>_Project_Creator
    ```

###### CREATE_PROJECT SCRIPT
  * add the options you need to the option parser in the ```if __name__ == 
    "__main__"``` section
  * in the ```create_project``` function, add the new language to the 
    **Project_Creator** object generation:
    ```python
    [...]
    elif language == "<new_language>":
        pj = <new_language>_Project_Creator()
    [...]
    ```
