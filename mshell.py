#!/usr/bin/python
#                                                                                                             
#   Copyright (c) 2010 Freetalk Python                                                                         
#   This file is part of freetalkpy.                                                                          
#                                                                                                             
#   FreetalkPy is free software; you can redistribute it and/or                                                
#   modify it under the terms of the GNU General Public License as                                             
#   published by the Free Software Foundation; either version 3 of                                             
#   the License, or (at your option) any later version.                                                         

#   FreetalkPy is distributed in the hope that it will be useful, but                                          
#   WITHOUT ANY WARRANTY; without even the implied warranty of                                                 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU                                          
#   General Public License for more details.                                                                    

#   You should have received a copy of the GNU General Public License                                          
#   along with this program.  If not, see                                                                      
#   <http://www.gnu.org/licenses/>.  

# -*- coding: utf-8 -*-
"""Framework for a minimal shell.
"""

__author__ = ""
__email__ = ""
__version__ = "0.1"
__copyright__ = ""
__license__ = "Python"
__status__ = "Production"

import exceptions
import grp
import os
import pwd
import shlex
import signal
import subprocess
import sys
import threading
import time

class ExitException(exceptions.BaseException):
	""""exit" command is given to the shell."""
	pass

class SIGINTException(exceptions.BaseException):
	"""SIGINT has been received."""
	pass

class MShell:
	"""A primitive interactive shell."""

	def __init__(self):
		"""Initializes shell."""
		signal.signal(signal.SIGINT, self.sigint_handler)

	def run(self):
		"""Starts the infinite loop for receiving input
		until one of the exceptions is raised.
		"""
		while(True):
			try:
				prompt = "[harshavardhanacool@gmail.com]>> "
				command = raw_input(prompt)
				args = shlex.split(command)

				if args[0] == "exit":
					raise ExitException

				callback = getattr(self,
						"on_%s" % args[0],
						self.default)

				if args[-1][-1] == "&":
					if len(args[-1]) > 1:
						args[-1] = args[-1][:-1]
					else:
						args = args[:-1]
					t = threading.Thread(
						target = callback,
						args = args)
					t.start()
				else:
					callback(*args);

			except IndexError:
				continue

			except EOFError:
				print "<EOF received, bye-bye>"
				return 0

			except ExitException:
				print "<exit called, bye-bye>"
				return 0

			except SIGINTException:
				print >> sys.stderr, \
					"<SIGINT received, bye-bye>"
				return 1

	def sigint_handler(self, signum, frame):
		"""Handler for the SIGINT signal."""
		raise SIGINTException

	def default(self, *args):
		"""Default handler for programs that aren't recognized as
		internal commands. Passes arguments to the child program.
		"""
		try:
			proc = subprocess.Popen(args,
				executable = args[0],
				stdin = sys.stdin,
				stdout = sys.stdout,
				stderr = sys.stderr)

		except OSError, e:
			print e

		else:
			print "Executing child process", proc.pid
			proc.wait()

	def on_ls(self, *args):
		"""Handle the internal "ls" command.
		
		Arguments:
		"-a" -- show hidden objects
		"-l" -- show detailed listing
		"-al" or "-la" -- show hidden objects and detailed listings
		[directory] -- path for the directory to list
		"""
		path = (not args[-1] in ["ls", "-a", "-l", "-al", "-la"]) \
			and args[-1] or "."
		all = "-a" in args or "-al" in args or "-la" in args
		long = "-l" in args or "-al" in args or "-la" in args

		try:
			contents = [i for i in os.listdir(path)
				if all or i[0] != '.']

		except OSError, e:
			print >> sys.stderr, e

		else:
			if not long:
				print "\n".join(contents)
			else:
				long_contents = \
					self.prepare_long_contents(path,
						contents)
				print "\n".join(long_contents)

	def on_cd(self, *args):
		"""Handle the internal "cd" command.
		
		Arguments:
		[Directory] -- Path to the new directory
		"""
		try:
			os.chdir(args[1])

		except OSError, e:
			print >> sys.stderr, e

	def prepare_long_contents(self, path, contents):
		"""Prepare detailed listings for direcotry contents.

		Keyword arguments:
		path -- path to the directory being listed
		contents -- list of objects in the directory
		"""
		long_contents = []

		for obj in contents:
			obj = os.path.join(path, obj)
			is_dir = os.path.isdir(obj) and "d" or "-"
			stats = os.stat(obj)

			perms = [False] * 9
			for i in range(9):
				perms[i] = bool(stats.st_mode & (1 << i)) \
					and "xwr"[i % 3] or "-"
			perms.reverse()

			user = pwd.getpwuid(stats[4]).pw_name
			group = grp.getgrgid(stats[5]).gr_name
			mtime = time.localtime(stats[8])

			long_contents.append("%s%s\t%s\t%s\t%s\t%s" % \
					(is_dir,
					"".join(perms),
					user,
					group,
					time.strftime("%Y-%m-%d %H:%M",
						mtime),
					obj))

		return long_contents

if __name__ == "__main__":
	sys.exit(MShell().run())

