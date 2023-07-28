# conda-shell-hook
Conda shell hook is a library that can be used to activate, deactivate and reactivate conda environments through the use of plugins.

Using plugins for activation allows conda to be used with shells that are not currently covered by conda's default activation logic. It also allows for the use of plugins that activate environments using different logic than the method currently in use.

Plugins ending in `_cl` use logic that is compatible with conda's current activation logic. Plugins ending in `_ose` use logic that differs from conda's current activation logic in two key ways:
- Environment activation is achieved by updating the environment mapping and replacing the Python process using an `os.exec*` function, instead of printing commands to `stdout` or evaluating them from a temporary file. This means that the newly activated conda environment is in a different shell process than the former environment; this is evidenced by an increased value of the `SHLVL` environment variable.
- Because environment activation takes place in a new shell process, only exported environment variables and functions will be carried forward to the new environment. Environment variables and functions that have been set but not exported will be lost during the environment activation/deactivation process.


## Installation
```conda install kalawac::condact```

## Usage
Currently, plugins are available for POSIX shells, with one plugin specifically intended for use only with Bash. Please read the plugin-specific usage instructions for each plugin (as applicable) prior to attempted use.

The names of the available plugins are listed below, alongside the shells they work with:
| Plugin Name | Shell(s) | Usage Instructions |
| ----------- | ----------- | ----------- |
| `posix_cl` | POSIX shells: `ash`, `bash`, `dash`, `ksh`, `sh`, `zsh` | [section] |
| `posix_ose` | POSIX shells: `ash`, `bash`, `dash`, `ksh`, `sh`, `zsh` | [section] |
| `bash_ose` | `bash` | None |

For the commands below, the following are placeholders:<br />
*`<ENVNAME>`* = conda environment name<br />
*`<PLUGIN>`* = shell plugin name<br />
*`<PREFIX>`* = conda environment path


### Activate an environment
Use either option below:
- ```conda shell -n <PLUGIN> activate <ENVNAME>```
- ```conda shell -n <PLUGIN> activate <PREFIX>```

### Deactivate an environment
```conda shell -n <PLUGIN> deactivate```

If an `os.exec*` plugin was used to activate the current environment, you may also exit the environment by using `ctrl + D` or your shell's `exit` command. However, deactivate scripts will not be run if you use this method.

### Reactivate an environment
```conda shell -n <PLUGIN> reactivate```

## Plugin-Specific Usage Instructions
