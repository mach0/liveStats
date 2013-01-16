# LiveStats #

**Disclaimer** : use at your own risk, the plugin is in developpement. In case of problem, open your QGis file in a plain text editor, and remove everything between &lt;LiveStats&gt; and &lt;/LiveStats&gt;.

## Description ##

LiveStats allows to display simple statistics about vector data in small toolbars that provide real-time feedback.

![Screenshot](https://raw.github.com/redlegoreng/liveStats/master/screenshot.png)


## Usage ##

Click on the LiveStats button to add a LiveStat. A configuration dialog will pop up.
Once configured, the statistic will be displayed at the bottom of the main window. You can move it around if you like and even display it as a floating palette.

Click on the LiveStats palette to modify it's settings again. You can add as many LiveStats palettes as you like. You can move them around, and dock/undock them. You can hide them like you do for any toolbar (right-click on an empty space of the interface).

The LiveStats automatically update when the selection changes (if "Selection only" is checked), when the active layer changes (if layer is set to "[active]"), when modified (by clicking on it), or when the project is opened.

### Configuration ###

- **Name** : Enter the display name of the statistic. You can check the box on the right to have an automatic name.
- **Layer** : Choose which layer the statistic will be based on. By choosing [active], the statistic will dynamically update depending on the current active layer.
- **Field** : Choose which field will be computed.
- **Filter** : Enter an SQL "where" expression to filter the features. Leave this empty if you don't want to filter the features.
- **Function** : Choose which statistic function you want to use. **Note that "count" simply counts the items, includings Null values** (this will be changed).
- **Selection only** : Check this if you want to compute statistics of the selection only. Leaving this unchecked will compute the statistics of the whole layer.
- **Precision...** : Enter the number of decimals, the suffix (usefull to specify a display unit), the factor (usefull to convert to a specific unit) and whether thousands separators should be shown
- **Save with project** : Check this to have the statistic saved into the project file and be reloaded next time you open it. Unchecking this and reloading the project is currently the only way to delete a LiveStat.
- **Copy** : If this is checked when clicking OK, the LiveStat will be copied into a new one, and the original one will remain untouched.



## Feedback / bugs ##

Please send bugs and ideas on the issue tracker : https://github.com/redlegoreng/liveStats/issues

Or send me some feedback at : olivier.dalang@gmail.com


## Version history ##
- 2013-01-01 - version 0.1 : first version (still very sketchy)
- 2013-01-02 - version 0.11 : fixed a bug with locale
- 2013-01-03 - version 0.2 : 
    - added "where filters"
    - ability to clone a LiveStat toolbar
- 2013-01-15 - version 0.3 :
    - added help (via the plugin menu)
    - fixed a small bug where there was a NoGeometry error under certain circumstances
    - fixed clone checkbox staying checked


## Contribute ##

Help is welcome ! There's a serie of issues and ideas on the github repository : https://github.com/redlegoreng/liveStats.git


