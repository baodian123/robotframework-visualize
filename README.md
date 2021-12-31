# robotframework-visualize

To visualize keyword structure including currently running script keyword and its children keyword.

## Function

``Pause`` button denote pause the execution after currently running keyword executed.

``Resume`` button denote resume the execution.

``Step Into`` button denote execute children keyword step by step.

``Step Over`` button denote execute keyword until next script keyword is executed.

``Render/On/Off`` button denote that whether to render the element which keyword manipulate.

``Scrollbar`` can adjust the transparency of control panel.

## Prerequisites

- **robotframework 3.2.2**
- **robotframework-seleniumlibrary 4.5.0**
- **pywin32**

# Usage

```
$ python -m robot --listener path/to/visualize_listener.py path/to/testfile.robot
```