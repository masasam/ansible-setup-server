#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>, and others
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import copy
import sys
import datetime
import traceback
import glob
import re
import shlex
import os

DOCUMENTATION = '''
---
module: commander
short_description: idempotency Executes a command on a remote node for ansible2
options:
  command:
    description:
      - the command module takes a free form command to run.
        See the examples!
    required: true
    default: null
  test_command:
    description:
      - the test command module takes a free form command to run.
        this test_command is executed before command is run,
        and this test_command is executed after command is run.
        See the examples!
    required: true
    default: null
  test_command_msg:
    description:
      - expect value of stdout or stderr in test_command.
        before command is run. when stdout or stderr in test_command doesn't include test_command_msg, module return fail.
        after command is run. when stdout or stderr in test_command include test_command_msg, module return success.
        See the examples!
    required: null
    default: null
  test_command_rc:
    description:
      - expect value of stdout or stderr in test_command.
        before command is run. when stdout or stderr in test_command doesn't include test_command_msg, module return fail.
        after command is run. when stdout or stderr in test_command include test_command_msg, module return success.
        See the examples!
    required: null
    default: null
  chdir:
    description:
      - cd into this directory before running the command
    version_added: "0.6"
    required: false
    default: null
'''

EXAMPLES = '''
  - name: sample repo
    commander:
    args:
      command: |
        cd /mnt/iscsi/svn
        svnadmin create sample
        chown -R apache:apache sample
      test_command: |
        test -e /mnt/iscsi/svn/sample/
      test_command_rc: "0"

  - name:  bundle install
    commander:
    args:
      command: |
        cd /var/lib/redmine
        source /root/.bash_profile
        bundle install
      test_command: |
        cd /var/lib/redmine
        bundle check
      test_command_msg: "dependencies are satisfied"
'''

# Dict of options and their defaults
OPTIONS = {'chdir': None,
           'executable': None,
           'NO_LOG': None,
           'check_mode': None,
           'command': None,
           'test_command': None,
           'test_command_msg': None,
           'test_command_rc': '0',
           }

# This is a pretty complex regex, which functions as follows:
#
# 1. (^|\s)
# ^ look for a space or the beginning of the line
# 2. ({options_list})=
# ^ expanded to (chdir|creates|executable...)=
#   look for a valid param, followed by an '='
# 3. (?P<quote>[\'"])?
# ^ look for an optional quote character, which can either be
#   a single or double quote character, and store it for later
# 4. (.*?)
# ^ match everything in a non-greedy manner until...
# 5. (?(quote)(?<!\\)(?P=quote))((?<!\\)(?=\s)|$)
# ^ a non-escaped space or a non-escaped quote of the same kind
#   that was matched in the first 'quote' is found, or the end of
#   the line is reached
OPTIONS_REGEX = '|'.join(OPTIONS.keys())
PARAM_REGEX = re.compile(
    r'(^|\s)(' + OPTIONS_REGEX +
    r')=(?P<quote>[\'"])?(.*?)(?(quote)(?<!\\)(?P=quote))((?<!\\)(?=\s)|$)'
)


def main():

    # the command module is the one ansible module that does not take key=value args
    # hence don't copy this one if you are looking to build others!

    module = AnsibleModule(
        argument_spec=dict(
          _raw_params = dict(),
          _uses_shell = dict(type='bool', default=False),
          chdir = dict(),
          executable = dict(),
          command = dict(),
          test_command = dict(),
          test_command_msg = dict(),
          test_command_rc = dict(),
        ),
        supports_check_mode = True
    )

    shell = True
    chdir = module.params['chdir']
    executable = module.params['executable']
    command  = module.params['command']
    test_command  = module.params['test_command']
    test_command_msg  = module.params['test_command_msg']
    test_command_rc  = module.params['test_command_rc']

    if not command:
        module.fail_json(rc=256, msg="no command given")

    if command.strip() == '':
        module.fail_json(rc=256, msg="no command given")

    if chdir:
        chdir = os.path.abspath(os.path.expanduser(chdir))
        os.chdir(chdir)

    if test_command:
        if test_command_rc is None and test_command_msg is None:
            module.fail_json(rc=256, msg="no test_command_rc: given")
        rc_test, out_test, err_test = module.run_command(test_command, executable=executable, use_unsafe_shell=shell)
        if test_command_rc is not None and test_command_rc == str(rc_test):
            module.exit_json(
                cmd      = command,
                shell    = shell,
                test_command = test_command, 
                test_command_rc = test_command_rc,
                stdout   = out_test,
                stderr   = err_test,
                changed=False,
                rc=rc_test
            )
        if test_command_msg is not None and (test_command_msg in out_test or test_command_msg in err_test): 
            module.exit_json(
                cmd      = command,
                shell    = shell,
                test_command = test_command, 
                test_command_msg = test_command_msg,
                stdout   = out_test,
                stderr   = err_test,
                changed=False,
                rc=rc_test
            )
             

    if not shell:
        command = shlex.split(command)

    startd = datetime.datetime.now()

    if module.check_mode:
        module.exit_json(
            cmd      = command,
            stdout   = '',
            stderr   = '',
            rc       = 0,
            changed  = True
        )

    rc, out, err = module.run_command(command, executable=executable, use_unsafe_shell=shell)
    if rc != 0:
       module.fail_json(
           cmd      = command,
           msg="failed execute command" +  "\n***command:\n" + command  + "\n***rc\n" + str(rc) + "\n***stdout\n" + out + "\n***stderr\n" + err,
           rc=256
       )

    endd = datetime.datetime.now()
    delta = endd - startd

    if out is None:
        out = ''
    if err is None:
        err = ''

    if test_command:
        if test_command_rc is None and test_command_msg is None:
            module.fail_json(rc=256, msg="no test_command_rc: given")
        rc_test, out_test, err_test = module.run_command(test_command, executable=executable, use_unsafe_shell=shell)
        if out_test is None:
            out_test = ''
        if err_test is None:
            err_test = ''
        if test_command_rc is not None and test_command_rc != str(rc_test):
            module.exit_json(
                stdout="failed test command after execute command" + "\n***command:\n" + command  + "\n***stdout\n" + out + "\n***stderr\n" + err + "\n***rc\n" + str(rc) + "\n***test_command\n" + test_command + "\n***stdout\n" + out_test + "\n***stderr\n" + err_test + "\n***rc\n" + str(rc_test),
                rc=256
            )
        if test_command_msg is not None and (test_command_msg not in out_test and test_command_msg not in err_test): 
            module.exit_json(
                stdout="failed test command after execute command" + "\n***command:\n" + command  + "\n***stdout\n" + out + "\n***stderr\n" + err + "\n***rc\n" + str(rc) + "\n***test_command\n" + test_command + "\n***stdout\n" + out_test + "\n***stderr\n" + err_test + "\n***rc\n" + str(rc_test),
                rc=256
            )

    module.exit_json(
        cmd      = command,
        test_command = test_command,
        test_command_msg = test_command_msg,
        stdout   = out,
        stderr   = err,
        rc       = rc,
        start    = str(startd),
        end      = str(endd),
        delta    = str(delta),
        changed  = True,
    )

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.splitter import *

main()
