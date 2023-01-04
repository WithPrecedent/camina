"""
base: base classes for extensible, flexible, lightweight containers
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Bunch (Collection, abc.ABC): base class for general containers in camina. 
        It requires subclasses to have 'add', 'delete', and 'subset' methods.
    Proxy (Container): basic wrapper for a stored python object. Dunder methods 
        attempt to intelligently apply access methods to either the wrapper or 
        the wrapped item.   
          
To Do:
    Fix Proxy setter. Currently, the wrapper and wrapped are not being set at
        the right time, likely due to the inner workings of 'hasattr'.
    Add more dunder methods to address less common and fringe cases for use
        of a Proxy class.
    
"""
from __future__ import annotations
import abc
from collections.abc import Collection, Container, Hashable, Iterator
import dataclasses
from typing import Any, Optional

  
@dataclasses.dataclass
class Bunch(Collection, abc.ABC):
    """Base class for general camina collections.
  
    A Bunch differs from a general python Collection in 4 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the collection. 'add' allows a subclass to 
            designate the preferred method of adding to the collections's stored 
            data without replacing other access methods.
        2) It must include a 'delete' method which provides the default
            mechanism for deleting items in the collection. 'delete' is called 
            by the '__delitem__' dunder method to delete stored items.
        3) A subclass must include a 'subset' method with optional 'include' and
            'exclude' parameters for returning a subset of the Bunch subclass.
        4) It supports the '+' operator being used to join a Bunch subclass 
            instance of the same python type (mapping, sequence, tuple, etc.). 
            The '+' operator calls the Bunch subclass 'add' method to implement 
            how the added item(s) is/are added to the Bunch subclass instance.

    Args:
        contents (Collection[Any]): stored collection of items.
              
    """
    contents: Collection[Any]
   
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def add(self, item: Any, *args: Any, **kwargs: Any) -> None:
        """Adds 'item' to 'contents'.
    
        Args:
            item (Any): item to add to 'contents'.
              
        """
        pass
            
    @abc.abstractmethod
    def delete(self, item: Any, *args: Any, **kwargs: Any) -> None:
        """Deletes 'item' from 'contents'.
        
        Args:
            item (Any): item or key to delete in 'contents'.
        
        Raises:
            KeyError: if 'item' is not in 'contents'.
            
        """
        pass
        
    @abc.abstractmethod
    def subset(
        self, 
        include: Optional[Collection[Any] | Any] = None, 
        exclude: Optional[Collection[Any] | Any] = None,
        *args: Any, 
        **kwargs: Any) -> Bunch:
        """Returns a new instance with a subset of 'contents'.
         
        This method applies 'include' before 'exclude' if both are passed. If
        'include' is None, all existing items will be added to the new subset
        class instance before 'exclude' is applied.
             
        Args:
            include (Optional[Collection[Any] | Any]): item(s) to include in the 
                new Bunch. Defaults to None.
            exclude (Optional[Collection[Any] | Any]): item(s) to exclude from 
                the new Bunch. Defaults to None.
        
        """
        pass
       
    """ Dunder Methods """
          
    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(item = other)
        return
    
    def __iadd__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(item = other)
        return
    
    def __delitem__(self, item: Hashable) -> None:
        """Deletes 'item' from 'contents'.
        
        Args:
            item (Any): item or key to delete in 'contents'.
        
        Raises:
            KeyError: if 'item' is not in 'contents'.
            
        """
        self.delete(item = item)
        return
    
    def __iter__(self) -> Iterator[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterator: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)  


@dataclasses.dataclass
class Proxy(Container):
    """Mostly transparent wrapper class.
    
    A Proxy differs than an ordinary container in 2 significant ways:
        1) Access methods for getting, setting, and deleting that try to 
            intelligently direct the user's call to the proxy or stored object.
            So, for example, when a user tries to set an attribute on the proxy,
            the method will replace an attribute that exists in the proxy if
            one exists. But if there is no such attribute, the set method is
            applied to the object stored in 'contents'.
        2) When an 'in' call is made, the '__contains__' method first looks to
            see if the item is stored in 'contents' (if 'contents' is a 
            collection). If that check gets an errorr, the method then checks
            if the item is equivalent to 'contents'. This allows a Proxy to be
            agnostic as to the type of item(s) in 'contents' while returning the
            expected result from an 'in' call.

    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
        
    ToDo:
        Add more dunder methods to address less common and fringe cases for use
            of a Proxy class.
        
    """
    contents: Optional[Any] = None

    """ Dunder Methods """
       
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equivalent to 'contents'.

        Args:
            item (Any): item to check versus 'contents'.
            
        Returns:
            bool: if 'item' is in or equivalent to 'contents' (True). Otherwise, 
                it returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            try:
                return item is self.contents
            except TypeError:
                return item == self.contents
                
    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'contents'.
        
        If 'attribute' exists in the Proxy subclass, this method will not be 
        called and the contents of that attribute will be returned.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if 'attribute' is not found in 'contents'.
        Returns:
            Any: matching attribute from 'contents'.

        """
        return getattr(self.contents, attribute)
        # try:
        #     return object.__getattribute__(
        #         object.__getattribute__(self, 'contents'), attribute)
        # except AttributeError:
        #     print('test no attribute in proxy', attribute)
        #     try:
        #         return object.__getattribute__(self, attribute)
        #     except AttributeError:
        #         raise AttributeError(
        #             f'{attribute} was not found in '
        #             f'{object.__getattribute__(self, "__name__")}') 

    # def __setattr__(self, attribute: str, value: Any) -> None:
    #     """Sets 'attribute' to 'value'.
        
    #     If 'attribute' exists in this class instance, its new value is set to
    #     'value.' Otherwise, 'attribute' and 'value' are set in what is stored
    #     in 'contents', whether the attribute previously existed in 'contents'.

    #     Args:
    #         attribute (str): name of attribute to set.
    #         value (Any): value to store in the attribute 'attribute'.

    #     """
    #     print('test hasattr', self, attribute)
    #     if self.contents is None or attribute not in dir(self.contents):
    #         print('test setting wrapper', value)
    #         object.__setattr__(self, attribute, value)
    #     else:
    #         print('test setting wrapped', value)
    #         object.__setattr__(self.contents, attribute, value)
            
    # def __delattr__(self, attribute: str) -> None:
    #     """Deletes 'attribute'.
        
    #     If 'attribute' exists in this class instance, it is deleted. Otherwise, 
    #     this method attempts to delete 'attribute' from what is stored in 
    #     'contents'.

    #     Args:
    #         attribute (str): name of attribute to set.

    #     Raises:
    #         AttributeError: if 'attribute' is neither found in the Proxy 
    #             subclass nor in 'contents'.
            
    #     """
    #     try:
    #         object.__delattr__(self, attribute)
    #     except AttributeError:
    #         try:
    #             object.__delattr__(self.contents, attribute)
    #         except AttributeError:
    #             raise AttributeError(
    #                 f'{attribute} was not found in '
    #                 f'{object.__getattribute__(self, "__name__")}')  
                   