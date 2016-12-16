## Unit testing requests :
From [SO](http://stackoverflow.com/questions/16864851/unit-testing-python-requests)
```python
import mock

from mymodule import my_method_under_test

class MyTest(TestCase):

    def test_request_get(self):
        with patch('requests.get') as patched_get:
            my_method_under_test()
            # Ensure patched get was called, called only once and with exactly these params.
            patched_get.assert_called_once_with("https://ec2.amazonaws.com/", params={'Action': 'GetConsoleOutput', 'InstanceId': 'i-123456'})
```

###Useful links

Submitting : 
- http://peterdowns.com/posts/first-time-with-pypi.html