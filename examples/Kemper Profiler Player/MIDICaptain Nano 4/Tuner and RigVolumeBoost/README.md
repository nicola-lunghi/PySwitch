## Exampe Description

|            | Action             |
|------------|--------------------|
| Switch 1   | Tuner Mode         |
| Switch 2   | Volume Boost (\*)  |
| Switch A   | Effect A           |
| Switch B   | Effect B           |

(\*) This volume boost works by settings the rig volume to a certain value (defined in switches.py in the action definition for RIG_VOLUME_BOOST). The controller remembers the default value of rig volume, and restores this value when the boost is switched off again. In this example, the rig volume will be set to +6dB when boost is activated.
