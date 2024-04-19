# Соглашения о коде

The style guide for Python is based on [Guido’s ](https://www.python.org/doc/essays/styleguide/)naming convention recommendations.

#### Наименования

| Type | Public               | Internal |
| :--- |:---------------------| :--- |
| Packages | `lower_with_under`   |  |
| Modules | `lower_with_under`   | `_lower_with_under` |
| Classes | `CapWords`           | `_CapWords` |
| Exceptions | `CapWords`           |  |
| Functions | `camelCase()`        | `camelCase()`  |
| Global/Class Constants | `CAPS_WITH_UNDER`    | `_CAPS_WITH_UNDER` |
| Global/Class Variables | `lower_with_under`   | `_lower_with_under` |
| Instance Variables | `lower_with_under`   | `_lower_with_under` |
| Method Names |`camelCase()`  | `camelCase()`  |
| Function/Method Parameters | `lower_with_under`   |  |
| Local Variables | `lower_with_under`   |  |

#### Типизация

 - типизация переменных в функции: 
 ```def func(a: int) -> list[int]: ```

 - также можно делать типизацию внутри функций, явно указывая тип возвращаемой переменной: 
``` a: SomeType = some_func() ```

#### Комментарии и аннотации

Пишутся на **русском языке**

 - Классы и функции в них:
```
class SampleClass:
    """Summary of class here.

    Longer class information...
    Longer class information...

    
    :atrib likes_spam: A boolean indicating if we like SPAM or not.
    :atrib eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, likes_spam: bool = False):
        """Initializes the instance based on spam preference.

        :param likes_spam: Defines if instance exhibits this preference.
        """
        self.likes_spam = likes_spam
        self.eggs = 0

 ```
 - Блочные и встроенные комментарии
```
# We use a weighted dictionary search to find out where i is in
# the array.  We extrapolate position based on the largest num
# in the array and the array size and then do binary search to
# get the exact number.

if i & (i-1) == 0:  # True if i is 0 or a power of 2.
 ```
**Начало** комментария - **строчная** буква

