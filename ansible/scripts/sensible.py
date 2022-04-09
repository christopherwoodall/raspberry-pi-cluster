#! /usr/bin/env python3
#-*- coding:utf-8 -*-
import sys; sys.dont_write_bytecode = True;

import argparse
import itertools
import json
import math
import os
import subprocess
import textwrap

import curses
import curses.panel
import curses.textpad

from pathlib import Path
from pprint import pprint

import yaml


__app__ = "Sensible"
__description__ = "Ansible Playbook TUI"


#########################################
class Sensible:
  subscriptions = {
    'dir': {
      'validate': 'check_path',
      'notify':   'find_playbooks'
    }
  }

  def __init__(self,**kwargs):
    self.options = { }
    self.position = 0
    self.run_plays = False
    self.elements = {
      'title':  "Sensible - Ansible Playbook TUI",
      'chyron': {
        '<arrows>': "Move Selection",
        '<space>': "Select Playbooks",
        '<enter>': "Run Playbooks",
        '<q>': "Quit",
        '<a>': "About"
      }
    }

    for key, value in kwargs.items(): self.attach(key, value)

    curses.wrapper(self.run)
    if self.run_plays:
     self.run_playbooks()


  ############
  # Utils
  def attach(self, key, value):
    if key in self.subscriptions.keys():
      observer = self.subscriptions[key]
      observer_keys = observer.keys()
      if 'validate' in observer_keys:
        validate = getattr(self,  observer['validate'])
        if validate(value):
          setattr(self, key, value)
      if 'notify' in observer_keys:
        notify = getattr(self,  observer['notify'])
        setattr(self, *notify(value))
    else:
      raise Exception("[!] Invalid argument")

  def check_path(self, path):
    if not Path(path).is_dir():
      print("[!] Directory does not exist")
      sys.exit(1)
    return True

  ############
  # Playbooks
  def find_playbooks(self, playbook_dir):
    playbook_dir += '/playbooks'  # TODO: make this a configurable option
    playbooks = [None] * 1000     # TODO: better array creation...
    files = [ f for f in Path(playbook_dir).iterdir()
      if f.is_file() and f.suffix in ['.yml', '.yaml'] ]
    for f in files:
      parsed = self.build_metadata(f)
      if parsed:
        parsed['path'] = str(f)
        parsed['selected'] = False
        if type(parsed['index']) == int:
          playbooks[parsed['index']] = parsed
        else:
          playbooks.append(parsed)
    playbooks = list(filter(None, playbooks))
    if not playbooks:
      raise OSError(f"[!] No playbooks found in {playbook_dir}")
    return ['options', playbooks]

  def build_metadata(self, playbook_path):
      content  = Path(playbook_path).read_text()
      header   = self.extract_header(content)
      if not header:
          # TODO - Just pass it to ansible-playbook?
          print("[!] Not a sensible playbook")
          sys.exit(1)
      playbook = self.parse_playbook(content)
      metadata = {**header, **playbook}
      header['path'] = playbook_path
      header['selected'] = False
      return metadata

  def extract_header(self, content):
      """
      Extracts the sensible header from a playbook.
      """
      start_pattern = '### sensible ###'
      end_pattern   = '### /sensible ###'
      if start_pattern in content and end_pattern in content:
          extracted = content.partition(end_pattern)[0].rpartition(start_pattern)[2]
          extracted = extracted.replace("#", "")
          return yaml.load(extracted, Loader=yaml.SafeLoader)
      return False

  def parse_playbook(self, content):
      data = {
          'hosts':      str(),
          #'pre_tasks':  list(),
          'roles':      list(),
          'tasks':      list(),
          #'post_tasks': list(),
      }
      try:
        playbook = yaml.load(content, Loader=yaml.SafeLoader)[0]
      except:
        return data
      keys = playbook.keys()
      if 'hosts' in keys: data['hosts'] = playbook['hosts']
      for key in data.keys():
          if key in keys:
              if key == 'hosts':
                  data[key] = playbook[key]
              elif key == 'tasks':
                  data[key] = [task['name'] for task in playbook[key] if 'name' in task]
              elif key == 'roles':
                  data[key] = [task['role'] for task in playbook[key] if 'role' in task]
      return data


  def run_playbooks(self):
    for option in self.options:
      ansible_cmd  = [ f"cd {self.dir} &&" ]
      ansible_cmd += [ f"ansible-playbook" ]
      if option['selected']:
        if 'vars' in option.keys():
          ansible_cmd += option['vars']
        playbook_path = option['path']
        ansible_cmd += [ f"playbooks/{playbook_path.split('/')[-1]}" ]
        os.system(' '.join(ansible_cmd))


  ############
  #
  def get_height( self ):
    height = int( os.popen('stty size').read( ).split( )[0].strip( ) )
    return height

  def get_width( self ):
    width = int( os.popen('stty size').read( ).split( )[1].strip( ) )
    return width

  ############
  #
  def center_text(self, text, width):
    return int((width // 2) - (len(text) // 2) - len(text) % 2)

  def slice_text(self, text, width, padding):
    text   = text.strip()
    if len(text) < (width - padding): return [text]
    sliced = []
    line = str()
    parts = list(itertools.chain.from_iterable(zip(text.split(), itertools.repeat(' '))))[:-1]
    for part in parts:
      if len(line) + len(part) < (width - padding):
        line += part
      else:
        sliced.append(line)
        line = part
      if part == parts[-1]:
        sliced.append(line)
    #sliced.append('...')
    return sliced

  def create_window(self, h, w, x, y, color=7 ):
    window = curses.newwin( h, w, x, y )
    window.erase()
    window.immedok(True)
    window.box()
    window.bkgd(" ", curses.color_pair(color))
    window.refresh( )
    return window

  def generate_list_item(self, window, item, index, max_x):
    highlight = self.WHITE

    if item['selected']:
      highlight =  self.GREEN

    if index == self.position:
      if not item['selected']:
        highlight = self.DIM_BLUE
      window.addstr((index + 2), 2, f"> ", highlight)

    # Check if selection is a seperator
    if 'seperator' in item['tags']:
      highlight = self.DIM_MAGENTA
      if index == self.position:
        highlight = self.MAGENTA
      padding = self.center_text(item['name'], max_x)
      window.addstr((index + 2), 4, f"{'-' * (max_x - 6)}", highlight)
      window.addstr((index + 2), (padding - 2), f" {item['name']} ", highlight)
      return

    # Check if selection is 'work in progress'
    if 'wip' in item['tags']:
      highlight = self.DIM_RED
      if index == self.position:
        highlight = self.RED

    window.addstr((index + 2), 4, f"{item['name']}", highlight)


  ############
  #
  def render_title(self):
    text = self.elements['title']
    height, width = self.stdscr.getmaxyx()
    start_y = int((width // 2) - (len(text) // 2) - len(text) % 2)
    self.stdscr.addstr(0, 0, f"{' ' * self.get_width()}", self.CONTRAST)
    self.stdscr.addstr(0, start_y, text, self.CONTRAST)

  def render_chyron(self):
    text = " | ".join(f'{k}: {v}' for k,v in self.elements['chyron'].items())
    height, width = self.stdscr.getmaxyx()
    self.stdscr.addstr(height-1, 0, " " * (width-1), self.CONTRAST)
    self.stdscr.addstr(height-1, 0, text, self.CONTRAST)

  def render_left_panel(self):
    max_x = math.floor(((self.get_width() / 9 )) * 6 )
    max_y = math.floor((self.get_height() -2))
    window = self.create_window( max_y, max_x, 1, 0 )
    for i, option in enumerate(self.options):
      self.generate_list_item(window, option, i, max_x)
    panel = curses.panel.new_panel(window)
    return window, panel

  def render_right_panel(self):
    cols = math.floor(((self.get_width() / 9 )) * 6 )
    max_x = math.floor(((self.get_width() / 9 )) * 3 )
    max_y = (self.get_height() -2)
    window = self.create_window(max_y, max_x, 1, cols)
    cur_selection = self.options[self.position]
    fields  = ['name', 'description', 'hosts', 'roles', 'tasks', 'tags']
    content = []
    for field in fields:
      if field in cur_selection.keys():
        value = cur_selection[field]
        if type(value) == list:
          value = ', '.join(value)
        line = f"{field.capitalize()}: {value}"
        content += self.slice_text(line, max_x, 4)

    for i, line in enumerate(content):
      window.addstr((i + 2), 2, f"{line}", self.DIM_CYAN)
    panel = curses.panel.new_panel(window)
    return window, panel


  ############
  # TUI
  def run(self, stdscr):
    self.stdscr = stdscr
    self.stdscr.border( 0 )
    self.stdscr.keypad(1)

    curses.noecho()
    curses.cbreak()
    curses.curs_set( 0 )

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)

    self.DIM_BLUE = curses.color_pair(1)
    self.DIM_RED = curses.color_pair(2)
    self.DIM_GREEN = curses.color_pair(3)
    self.DIM_MAGENTA = curses.color_pair(4)
    self.DIM_CYAN = curses.color_pair(5)
    self.DIM_YELLOW = curses.color_pair(6)
    self.DIM_WHITE = curses.color_pair(7)

    self.BLUE = curses.color_pair(1) | curses.A_BOLD
    self.RED = curses.color_pair(2) | curses.A_BOLD
    self.GREEN = curses.color_pair(3) | curses.A_BOLD
    self.MAGENTA = curses.color_pair(4) | curses.A_BOLD
    self.CYAN = curses.color_pair(5) | curses.A_BOLD
    self.YELLOW = curses.color_pair(6) | curses.A_BOLD
    self.WHITE = curses.color_pair(7) | curses.A_BOLD
    self.CONTRAST = curses.color_pair(8) | curses.A_BOLD

    k = 0
    cursor_y = 0
    cursor_y_max = len(self.options) -1

    while (k != ord('q')):
      stdscr.clear()
      stdscr.refresh()

      if k == curses.KEY_DOWN:
        if (cursor_y + 1) >= cursor_y_max:
          cursor_y = cursor_y_max
        else:
          cursor_y += 1
      elif k == curses.KEY_UP:
        if (cursor_y - 1) < 0:
          cursor_y = 0
        else:
          cursor_y -= 1

      elif k == ord(' '):
        if 'seperator' not in self.options[self.position]['tags']:
          self.options[self.position]['selected'] = (
            not self.options[self.position]['selected'] )
      elif k == curses.KEY_ENTER or k == 10:
        self.run_plays = True
        break

      self.position = cursor_y

      # Render title
      self.render_title()
      # Render status bar
      self.render_chyron()
      ## Window/Panel
      win1, panel1 = self.render_left_panel()
      curses.panel.update_panels(); stdscr.refresh()
      panel1.top(); curses.panel.update_panels(); stdscr.refresh()
      ## Window/Panel
      win1, panel2 = self.render_right_panel()
      curses.panel.update_panels(); stdscr.refresh()
      panel2.top(); curses.panel.update_panels(); stdscr.refresh()

      # Refresh the screen
      stdscr.refresh()

      # Wait for next input
      k = stdscr.getch()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    prog=__app__,
    description=__description__
  )

  parser.add_argument(
    "-d",
    "--dir",
    nargs='?',
    required=True,
    help=""
  )

  args = vars( parser.parse_args() )

  app = Sensible(**args)
