#--------------------------------------------------------------------------
#     This file is part of BKchem - a chemical drawing program
#     Copyright (C) 2004 Beda Kosata <beda@zirael.org>

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     Complete text of GNU GPL can be found in the file gpl.txt in the
#     main directory of the program

#--------------------------------------------------------------------------

import xml.dom.minidom as dom
import dom_extensions as dom_ext
import os_support
import os
import debug

from singleton_store import Store



class plugin_manager( object):

  def __init__( self):
    self.plugins = {}
    self.descriptions = {}

  def get_available_plugins( self):
    dir2 = os_support.get_dirs( 'plugin')
    dir1 = os_support.get_bkchem_private_dir()
    dir1 = os.path.join( dir1, 'plugins')
    dirs = dir2 + [dir1]
    for dir in dirs:
      if not os.path.isdir( dir):
        continue
      for name in os.listdir( dir):
        base, ext = os.path.splitext( name)
        if ext == ".xml":
          #try:
          self.read_plugin_file( dir, name)
          #except:
          #  debug.log( "could not load plugin file", name)

    return self.plugins.keys()



  def read_plugin_file( self, dir, name):
    doc = dom.parse( os.path.join( dir, name))
    root = doc.childNodes[0]
    plugin_type = root.getAttribute( 'type') or 'script'
    sources = dom_ext.simpleXPathSearch( doc, "/plugin/source")
    if sources:
      source = sources[0]
      files = dom_ext.simpleXPathSearch( source, "file")
      names = dom_ext.simpleXPathSearch( source, "menu-text")
      descs = dom_ext.simpleXPathSearch( source, "/plugin/meta/description")
      if files and names:
        file = dom_ext.getAllTextFromElement( files[0])
        if not os.path.isabs( file):
          file = os.path.normpath( os.path.join( dir, file))
        name = dom_ext.getAllTextFromElement( names[0])

        plugin = plugin_handler( name, file, type=plugin_type,
                                 desc=descs and dom_ext.getAllTextFromElement( descs[0]) or '')
        self.plugins[ name] = plugin



  def run_plugin( self, name):
    handler = self.plugins[ name]

    if handler.type == "script":
      filename = handler.filename
      the_globals = {'App': Store.app}
      execfile( filename, the_globals)
    else:
      raise ValueError, "Wrong type of plugin %s" % name



  def get_names( self, type=""):
    if not type:
      return self.plugins.keys()
    else:
      return [k for k, v in self.plugins.iteritems() if v.type == type]
    

  def get_description( self, name):
    handler = self.get_plugin_handler( name)
    if handler:
      return handler.desc
      return ''


  def get_plugin_handler( self, name):
    return self.plugins.get( name, None)


  

class plugin_handler:
  """this class stores information about plugin"""

  def __init__( self, name, filename, type="script", desc=""):
    self.name = name
    self.type = type
    self.desc = desc
    self.filename = filename

    
  def get_module_name( self):
    """returns name of module suitable for loading of this plugin via import"""
    return os.path.splitext( os.path.split( self.filename)[1])[0]


  def get_directory_name( self):
    """returns directory where the plugin resides"""
    return os.path.split( self.filename)[0]


  
