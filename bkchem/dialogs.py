#--------------------------------------------------------------------------
#     This file is part of BKchem - a chemical drawing program
#     Copyright (C) 2002, 2003 Beda Kosata <beda@zirael.org>

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
#
#
#
#--------------------------------------------------------------------------

"""set of dialogs used by BKchem"""

import Tkinter
import tkFont
import tkMessageBox
import Pmw
import misc
import data
import re
import widgets
import classes

## SCALE DIALOG

class scale_dialog:
  """dialog used to get ratio for scaling in percent"""
  def __init__( self, parent):
    self.dialog = Pmw.Dialog( parent,
                              buttons=(_('OK'), _('Cancel')),
                              defaultbutton=_('OK'),
                              title=_('Scale'),
                              command=self.done)
    # X RATIO
    self.entryx = Pmw.Counter( self.dialog.interior(),
                               labelpos = 'w',
                               label_text=_("Scale X (in %):"),
                               entryfield_value = 100,
                               entryfield_validate={ 'validator':'integer', 'min':1, 'max':1000},
                               entry_width = 5,
                               entryfield_modifiedcommand = self._scalex_changed,
                               increment = 10,
                               datatype = 'integer')
    self.entryx.pack(pady=10, anchor='w', padx=10)
    # Y RATIO
    self.entryy = Pmw.Counter( self.dialog.interior(),
                               labelpos = 'w',
                               label_text=_("Scale Y (in %):"),
                               entryfield_value = 100,
                               entryfield_validate={ 'validator':'integer', 'min':1, 'max':1000},
                               entry_width = 5,
                               entryfield_modifiedcommand = self._scaley_changed,
                               increment = 10,
                               datatype = 'integer')
    self.entryy.pack(pady=10, anchor='w', padx=10)

    self.preserve_ratio = Tkinter.IntVar()
    self.preserve_ratio_entry = Tkinter.Checkbutton( self.dialog.interior(),
                                                     text=_('Preserve aspect ratio?'),
                                                     variable = self.preserve_ratio,
                                                     command = self._preserve_ratio_changed)
    self.preserve_ratio_entry.pack()

    self.dialog.activate()

  def done( self, button):
    """called on dialog exit"""
    if not button or button == _('Cancel'):
      self.result = None
    elif not (self.entryx.valid() and self.entryy.valid()) :
      self.result = ()
    else:
      self.result = (float( self.entryx.get()), float( self.entryy.get())) #, self.preserve_center.get())
      if self.preserve_ratio.get():
        # x is significant if ratio should be preserved
        self.result = (self.result[0], self.result[0])
    self.dialog.deactivate()

  def _scalex_changed( self):
    if self.preserve_ratio.get():
      if self.entryy.get() != self.entryx.get():
        self.entryy.setentry( self.entryx.get())

  def _scaley_changed( self):
    if self.preserve_ratio.get():
      if self.entryy.get() != self.entryx.get():
        self.entryx.setentry( self.entryy.get())

  def _preserve_ratio_changed( self):
    if self.preserve_ratio.get():
      if self.entryy.get() != self.entryx.get():
        if self.entryx.get() == '100':
          self.entryx.setentry( self.entryy.get())
        else:
          self.entryy.setentry( self.entryx.get())
    

## CONFIG DIALOG

class config_dialog:
  """items configuration"""
  def __init__( self, parent, items):
    self.items = items
    self.changes_made = 0
    self.parent = parent
    self.dialog = Pmw.Dialog( parent,
                              buttons=(_('OK'), _('Cancel')),
                              defaultbutton=_('OK'),
                              title=_('Configuration'),
                              command=self.done,
                              master='parent')
    #parent.bind_all( "<Button-1>", self.raise_me, add='+')
    self.pages = Pmw.NoteBook( self.dialog.interior())
    self.pages.pack( anchor='w', pady=0, padx=0, fill='both', expand=1)
    
    # create pages for different item types
    self.atom_page = None
    self.bond_page = None
    self.arrow_page = None
    self.text_page = None
    self.plus_page = None
    self.font_page = None
    self.common_page = None
    arrows = []
    for o in items:
      if o.object_type == 'point':
        items.remove( o)
        if o.arrow not in arrows:
          arrows.append( o.arrow)
    items += arrows
    types = misc.filter_unique( [o.object_type for o in items])

    if 'atom' in types:
      self.atom_page = self.pages.add(_('Atom'))
      # charge
      charges = misc.filter_unique( [o.charge for o in items if o.object_type == 'atom'])
      if len( charges) == 1:
        charge = charges[0]
      else:
        charge = ''
      self.atom_charge = Pmw.Counter( self.atom_page,
                                      labelpos = 'w',
                                      label_text = _('Charge'),
                                      entryfield_value = charge,
                                      entryfield_validate={ 'validator':'integer', 'min':-4, 'max':4},
                                      entry_width = 3,
                                      increment = 1,
                                      datatype = 'integer')
      self.atom_charge.pack( anchor='nw', padx=10, pady=5)
      # show?
      shows = misc.filter_unique( [o.show for o in items if o.object_type == 'atom'])
      if len( shows) == 1:
        show = int( shows[0])
      else:
        show = 2 # means the show should be preserved as is
      self.atom_show = Pmw.OptionMenu( self.atom_page,
                                       labelpos = 'nw',
                                       label_text = _('Atom name'),
                                       items = (_("don't show"),_("show"),u""),
                                       initialitem = show)
      self.atom_show.pack( anchor = 'nw')
      # positioning
      poss = misc.filter_unique( [o.pos for o in items if o.object_type == 'atom'])
      if not poss:
        pos = None
      elif len( poss) == 1 and poss[0]:
        pos = ['center-first', 'center-last'].index( poss[0])
      else:
        pos = 2 # means the centering should be preserved as is
      if pos == None:
        self.atom_pos = None
      else:
        self.atom_pos = Pmw.OptionMenu( self.atom_page,
                                        labelpos = 'nw',
                                        label_text = _('Atom positioning'),
                                        items = (_("center first letter"),_("center last letter"), u""),
                                        initialitem = pos)

        self.atom_pos.pack( anchor = 'nw')
      # show hydrogens
      shows = misc.filter_unique( [o.show_hydrogens for o in items if o.object_type == 'atom'])
      if len( shows) == 1:
        show = shows[0]
      else:
        show = 2 # means the show should be preserved as is
      self.atom_show_h = Pmw.OptionMenu( self.atom_page,
                                         labelpos = 'nw',
                                         label_text = _('Hydrogens'),
                                         items = (_("off"),_("on"), u""),
                                         initialitem = show)

      self.atom_show_h.pack( anchor = 'nw')

      # marks
      #self.marks = widgets.GraphicalAngleChooser( self.atom_page, 270)
      #self.marks.pack()

    # BOND
    if 'bond' in types:
      self.bond_page = self.pages.add(_('Bond'))
      # bond_widths (former distances)
      dists = misc.filter_unique( map( abs, [o.bond_width for o in items if o.object_type == 'bond']))
      if len( dists) == 1:
        dist = dists[0]
      else:
        dist = ''
      if not misc.split_number_and_unit( dist)[1]:
        dist = str( dist) + 'px'
      self.bond_dist = widgets.WidthChooser( self.bond_page, dist, label=_('Bond width'))
      self.bond_dist.pack( anchor='ne', padx=10, pady=5)

      # wedge_widths
      dists = misc.filter_unique( map( abs, [o.wedge_width for o in items if o.object_type == 'bond']))
      if len( dists) == 1:
        dist = dists[0]
      else:
        dist = ''
      if not misc.split_number_and_unit( dist)[1]:
        dist = str( dist) + 'px'
      self.wedge_width = widgets.WidthChooser( self.bond_page, dist, label=_('Wedge/Hatch width'))
      self.wedge_width.pack( anchor='ne', padx=10, pady=5)


      # double bond length ratio
      ratios = misc.filter_unique( [o.double_length_ratio for o in items if o.object_type == 'bond'])
      if len( ratios) == 1:
        ratio = ratios[0]
      else:
        ratio = ''
      self.double_length_ratio = widgets.RatioCounter( self.bond_page,
                                                       ratio,
                                                       label=_('Double-bond length ratio'))
      self.double_length_ratio.pack( anchor='nw', padx=10, pady=5)



    # ARROW
    if 'arrow' in types:
      self.arrow_page = self.pages.add(_('Arrow'))
      self.arrow_end_changed = 0
      self.arrow_start_changed = 0
      arrow_items = [o for o in items if o.object_type == 'arrow']

      # arrow start pins
      arrow_starts = misc.filter_unique( [o.get_pins()[0] for o in arrow_items])
      self.arrow_start = Tkinter.IntVar()
      if len( arrow_starts) == 1:
        self.arrow_start.set( arrow_starts[0])
      else:
        self.arrow_start.set( 0)
      self.arrow_start_entry = Tkinter.Checkbutton( self.arrow_page,
                                                    text=_('Arrow-head on start'),
                                                    variable = self.arrow_start,
                                                    command = self._arrow_start_changed)
      self.arrow_start_entry.pack( anchor='w')

      # arrow end pins
      arrow_ends = misc.filter_unique( [o.get_pins()[1] for o in arrow_items])
      self.arrow_end = Tkinter.IntVar()
      if len( arrow_ends) == 1:
        self.arrow_end.set( arrow_ends[0])
      else:
        self.arrow_end.set( 0)
      self.arrow_end_entry = Tkinter.Checkbutton( self.arrow_page,
                                                  text=_('Arrow-head on end'),
                                                  variable = self.arrow_end,
                                                  command = self._arrow_end_changed)
      self.arrow_end_entry.pack( anchor='w')

      # spline?
      splines = misc.filter_unique( [o.spline for o in arrow_items])
      self.spline = Tkinter.IntVar()
      if len( splines) == 1:
        self.spline.set( splines[0])
      else:
        self.spline.set( 0)
      self.spline_entry = Tkinter.Checkbutton( self.arrow_page,
                                               text=_('Spline arrow'),
                                               variable = self.spline,
                                               command = self._spline_changed)
      self.spline_changed = 0
      self.spline_entry.pack( anchor='w')
      

    # TEXTS

    # PLUS

    # FONT
    if ('atom' in types) or ('text' in types) or ('plus' in types):
      self.font_page = self.pages.add(_('Font'))

      font_items = [o for o in items if o.object_type == 'atom' or o.object_type == 'text' or o.object_type == 'plus']
      sizes = misc.filter_unique( [o.font_size for o in font_items])
      if len( sizes) == 1:
        size = sizes[0]
      else:
        size = ''
      self.font_size = widgets.FontSizeChooser( self.font_page, size)
      self.font_size.pack( anchor = 'nw')

      used_families = misc.filter_unique( [o.font_family for o in font_items])
      if len( used_families) == 1:
        self.used_family = used_families[0]
      else:
        self.used_family = ''
      self.font_family = widgets.FontFamilyChooser( self.font_page, self.used_family)
      self.font_family.pack( anchor="nw", side = 'bottom')


    # COMMON
    self.common_page = self.pages.add(_('Common'))
    there_are_lines = 0
    for line_type in data.line_types:
      if line_type in types:
        there_are_lines = 1
        break
    if there_are_lines:
      line_items = [o for o in items if o.object_type in data.line_types]
      widths = misc.filter_unique( [o.line_width for o in line_items])
      if len( widths) == 1:
        width = widths[0]
      else:
        width = ''
      if not misc.split_number_and_unit( width)[1]:
        width = str( width) + 'px'
      self.line_width = widgets.WidthChooser( self.common_page, width, label=_('Line width'))
      self.line_width.pack( anchor='nw', padx=10, pady=5)

    line_color_items = [o for o in items if o.object_type in data.line_color_types]
    lines = misc.filter_unique( [o.line_color for o in line_color_items])
    if len( lines) == 1:
      line = lines[0]
    else:
      line = None
    self.line_color = widgets.ColorButton( self.common_page, color=line, text=_("Line color"))
    self.line_color.pack( anchor='nw', padx=10, pady=5)

    area_color_items = [o for o in items if o.object_type in data.area_color_types]
    areas = misc.filter_unique( [o.area_color for o in area_color_items])
    if len( areas) == 1:
      area = areas[0]
    else:
      area = None
    self.area_color = widgets.ColorButton( self.common_page, color=area, text=_("Area color"))
    self.area_color.pack( anchor='nw', padx=10, pady=5)


    # RUN IT ALL
    self.pages.setnaturalsize()
    self.dialog.activate( globalMode=0)


  def done( self, button):
    """called on dialog exit"""
    self.dialog.deactivate()
    if button != _('OK'):
      pass
    else:
      #print self.marks.get()
      # apply changes
      for o in self.items:
        change = 0
        # ATOM
        if o.object_type == 'atom':
          a = self.atom_show.index( Pmw.SELECT)
          if a != 2:
            o.show = a
            change = 1
          # positionning
          a = self.atom_pos.index( Pmw.SELECT)
          if a != 2:
            o.pos = ('center-first', 'center-last')[ a]
            change = 1
          if self.atom_charge.get():
            a = int( self.atom_charge.get())
            if o.charge != a:
              o.charge = a
            change = 1
          # hydrogens
          a = int( self.atom_show_h.index( Pmw.SELECT))
          if a != 2:
            o.show_hydrogens = a
            change = 1
          # font is in common now
        # BOND
        elif o.object_type == 'bond':
          # width is in common now
          # bond_width
          d = self.parent.paper.any_to_px( self.bond_dist.getvalue())
          if d:
            if d != abs( o.bond_width):
              o.bond_width = d * misc.signum( o.bond_width)
              change = 1
          # wedge_width
          d = self.parent.paper.any_to_px( self.wedge_width.getvalue())
          if d:
            if d != o.wedge_width:
              o.wedge_width = d
              change = 1
          # ratio
          ratio = self.double_length_ratio.getvalue()
          if ratio:
            ratio = float( self.double_length_ratio.getvalue())
            if ratio != o.double_length_ratio:
              o.double_length_ratio = ratio
              change = 1
            
        # ARROW - most is in common now
        elif o.object_type == 'arrow':
          if self.arrow_start_changed:
            o.set_pins( start = self.arrow_start.get())
            change = 1
          if self.arrow_end_changed:
            o.set_pins( end = self.arrow_end.get())
            change = 1
          if self.spline_changed:
            o.spline = self.spline.get()
            change = 1
            
        # TEXT - all is in common now
        # PLUS - all is in common now
        # VECTOR - all is in common now

        # COMMON PROPERTIES
        # LINE COLOR
        if o.object_type in data.line_color_types:
          if self.line_color.color:
            if self.line_color.color != o.line_color:
              o.line_color = self.line_color.color
              change = 1
        # AREA COLOR
        if o.object_type in data.area_color_types:
          if self.area_color.color:
            if self.area_color.color != o.area_color:
              o.area_color = self.area_color.color
              change = 1
        # LINE WIDTH
        if o.object_type in data.line_types:
          w = self.parent.paper.any_to_px( self.line_width.getvalue())
          if w:
            if w != o.line_width:
              o.line_width = w
              change = 1
        # FONT
        if o.object_type in data.font_types:
          if self.font_size.get():
            a = int( self.font_size.get())
            o.font_size = a
            change = 1
          if self.font_family.getcurselection() and self.font_family.getcurselection()[0] != self.used_family:
            a = self.font_family.getcurselection()[0]
            o.font_family = a
            change = 1
          
        # APPLY THE CHANGES
        if change:
          o.redraw()
          self.changes_made = 1
    self.cleanup()


  def _arrow_end_changed( self):
    self.arrow_end_changed = 1

  def _arrow_start_changed( self):
    self.arrow_start_changed = 1

  def _spline_changed( self):
    self.spline_changed = 1

  def raise_me( self, event):
    self.dialog.tkraise()

  def cleanup( self):
    pass
    #self.parent.unbind_all( "<Button-1>")


## -------------------- FILE PROPERTIES DIALOG --------------------

class file_properties_dialog:

  def __init__( self, parent, paper):
    self.parent = parent
    self.paper = paper
    self.dialog = Pmw.Dialog( parent,
                              buttons=(_('OK'), _('Cancel')),
                              defaultbutton=_('OK'),
                              title=_('File properties'),
                              command=self.done,
                              master='parent')
    self.body = Tkinter.Frame( self.dialog.interior())
    self.body.pack()
    self.draw()
    self.dialog.activate()

  def draw( self):
    # paper type
    if self.paper._paper_properties['type'] == 'custom':
      t = _('Custom')
    else:
      t = self.paper._paper_properties['type']
    self.paper_type_chooser = Pmw.OptionMenu( self.body,
                                              items=data.paper_types.keys(), #+[_('Custom')],
                                              initialitem = t,
                                              labelpos = 'w',
                                              label_text = _('Paper size')+':',
                                              menubutton_width = 10)
    self.paper_type_chooser.pack( anchor='w', padx=10, pady=10)
    # paper orientation
    self.paper_orientation_chooser = Pmw.RadioSelect( self.body,
                                                      buttontype='radiobutton',
                                                      orient='vertical',
                                                      pady=0)
    self.paper_orientation_chooser.add(_('Portrait'))
    self.paper_orientation_chooser.add(_('Landscape'))
    self.paper_orientation_chooser.pack( anchor='w', padx=10, pady=10)
    if self.paper._paper_properties['orientation'] == 'portrait':
      i = 0
    else:
      i = 1
    self.paper_orientation_chooser.invoke( i)
    # full svg or just the filled part
    self.crop_paper_in_svg = Tkinter.IntVar()
    self.crop_paper_in_svg.set( self.paper.get_paper_property( 'crop_svg'))
    crop = Tkinter.Checkbutton( self.body, text=_('Auto crop image in SVG?'), variable=self.crop_paper_in_svg)
    crop.pack( anchor='w', padx=10, pady=10)


  def done( self, button):
    self.dialog.deactivate()
    if button == _('OK'):
      if self.paper_orientation_chooser.getvalue() == _('Portrait'):
        o = 'portrait'
      else:
        o = 'landscape'
      type = self.paper_type_chooser.getvalue()
      if type == _('Custom'):
        type = 'custom'
      self.paper.set_paper_properties( type=type,
                                       orientation=o,
                                       crop_svg=self.crop_paper_in_svg.get())
      self.paper.changes_made = 1


##-------------------- STANDARD VALUES DIALOG --------------------

class standard_values_dialog:

  def __init__( self, parent, standard):
    self.parent = parent
    self.standard = standard
    self.dialog = Pmw.Dialog( parent,
                              buttons=(_('OK'), _('Cancel'), _('Save')),
                              defaultbutton=_('OK'),
                              title=_('Standard values'),
                              command=self.done,
                              master='parent')
    self.body = self.dialog.interior()
    #self.body.pack( fill='both', expand=1)
    self.draw()
    self.dialog.activate()

  def draw( self):
    self.pages = Pmw.NoteBook( self.body)
    self.pages.pack( anchor='w', pady=0, padx=0, fill='both', expand=1)
    # COMMON
    common_page = self.pages.add( _('Common'))
    # LINE
    line_group = Pmw.Group( common_page, tag_text=_('Line'))
    line_group.pack( fill='x')
    # line width
    self.line_width = widgets.WidthChooser( line_group.interior(), self.standard.line_width, label=_('Line width'))
    self.line_width.pack( anchor='nw', padx=10, pady=5)
    # COLORS
    color_group = Pmw.Group( common_page, tag_text=_('Color'))
    color_group.pack( fill='x')
    # line color
    self.line_color = widgets.ColorButton( color_group.interior(), color=self.standard.line_color, text=_("Line color"))
    self.line_color.pack( side='left', padx=10, pady=5)
    # area color
    self.area_color = widgets.ColorButton( color_group.interior(), color=self.standard.area_color, text=_("Area color"))
    self.area_color.pack( side='right', padx=10, pady=5)

    # BOND
    bond_group = self.pages.add( _("Bond")) #Pmw.Group( self.body, tag_text=_('Bond'))
    # bond width
    self.bond_width = widgets.WidthChooser( bond_group, self.standard.bond_width, label=_('Bond width'))
    self.bond_width.pack( anchor='ne', padx=10, pady=5)
    # wedge bond width
    self.wedge_width = widgets.WidthChooser( bond_group, self.standard.wedge_width, label=_('Wedge/Hatch width'))
    self.wedge_width.pack( anchor='ne', padx=10, pady=5)
    # bond length
    self.bond_length = widgets.LengthChooser( bond_group, self.standard.bond_length, label=_('Bond length'))
    self.bond_length.pack( anchor='ne', padx=10, pady=5)
    # double bond length ratio
    self.double_length_ratio = widgets.RatioCounter( bond_group,
                                                     self.standard.double_length_ratio,
                                                     label=_('Double-bond length ratio'))
    self.double_length_ratio.pack( anchor='ne', padx=10, pady=5)

    # FONT
    font_group = self.pages.add( _('Font'))
    # font size
    self.font_size = widgets.FontSizeChooser( font_group, self.standard.font_size)
    self.font_size.pack( anchor = 'nw')
    # font family
    self.font_family = widgets.FontFamilyChooser( font_group, self.standard.font_family)
    self.font_family.pack( anchor="nw", side = 'bottom')

    # paper type
    self.paper = self.parent.paper
    paper_group = self.pages.add(_('Paper'))
    if self.paper._paper_properties['type'] == 'custom':
      t = _('Custom')
    else:
      t = self.paper._paper_properties['type']
    self.paper_type_chooser = Pmw.OptionMenu( paper_group,
                                              items=data.paper_types.keys(), #+[_('Custom')],
                                              initialitem = t,
                                              labelpos = 'w',
                                              label_text = _('Paper size')+':',
                                              menubutton_width = 10)
    self.paper_type_chooser.pack( anchor='w', padx=10, pady=10)
    # paper orientation
    self.paper_orientation_chooser = Pmw.RadioSelect( paper_group,
                                                      buttontype='radiobutton',
                                                      orient='vertical',
                                                      pady=0)
    self.paper_orientation_chooser.add(_('Portrait'))
    self.paper_orientation_chooser.add(_('Landscape'))
    self.paper_orientation_chooser.pack( anchor='w', padx=10, pady=10)
    if self.paper._paper_properties['orientation'] == 'portrait':
      i = 0
    else:
      i = 1
    self.paper_orientation_chooser.invoke( i)
    # full svg or just the filled part
    self.crop_paper_in_svg = Tkinter.IntVar()
    self.crop_paper_in_svg.set( self.paper.get_paper_property( 'crop_svg'))
    crop = Tkinter.Checkbutton( paper_group, text=_('Auto crop image in SVG?'), variable=self.crop_paper_in_svg)
    crop.pack( anchor='w', padx=10, pady=10)

    # how to apply?
    apply_group = Pmw.Group( self.body, tag_text=_('Apply'))
    apply_group.pack( fill='x', padx=5, pady=5)
    # apply all or only the changed ones? - it must be created before apply_button because
    # of the callback that operates on activity of apply_button2
    self.apply_button2 = Pmw.RadioSelect( apply_group.interior(),
                                         buttontype = 'radiobutton',
                                         orient = 'vertical',
                                         pady = 0)
    self.apply_button2.add( _("changed values only"))
    self.apply_button2.add( _("all values"))
    self.apply_button2.invoke( 0)
    # apply to current drawing?
    self.apply_button = Pmw.RadioSelect( apply_group.interior(),
                                         buttontype = 'radiobutton',
                                         command = self._apply_button_callback,
                                         orient = 'vertical',
                                         pady = 0)
    self.apply_button.add( _("to new drawings only"))
    self.apply_button.add( _("to selected and new drawings (no resize)"))
    self.apply_button.add( _("to the whole drawing (no resize)"))
    self.apply_button.invoke( 0)
    self.apply_button.pack( padx=0, pady=0, anchor='w')
    # we pack the button2 here to get a better organization
    self.apply_button2.pack( padx=0, pady=10, anchor='w')

    self.pages.setnaturalsize()


  def done( self, button):
    if button == _('Save'):
      a = self.parent.paper.save_personal_standard( self.get_the_standard())
      if a:
        tkMessageBox.showinfo( _("Standard saved"),
                               _("The standard was successfully saved as personal standard to %s") % a)
      else:
        tkMessageBox.showerror( _("Standard not saved"),
                                _("""For some reason the standard couldn't be saved. Probably the right location
                                for personal profile couldn't be found or wasn't writable. Sorry for the inconvenience."""))
      return 
    self.dialog.deactivate()
    if button == _('OK'):
      self.standard = self.get_the_standard()
      self.apply = self.apply_button.index( self.apply_button.getvalue())
      self.apply_all = self.apply_button2.index( self.apply_button2.getvalue())
      self.change = 1
    else:
      self.change = 0
      self.apply_all = 0

  def get_the_standard( self):
    st = classes.standard()
    st.bond_width = self.bond_width.getvalue()
    st.line_width = self.line_width.getvalue()
    st.wedge_width = self.wedge_width.getvalue()
    st.bond_length = self.bond_length.getvalue()
    st.double_length_ratio = float( self.double_length_ratio.getvalue())
    st.line_color = self.line_color.color
    st.area_color = self.area_color.color
    st.font_family = self.font_family.getcurselection()[0]
    st.font_size = int( self.font_size.get())
    # paper properties
    # type
    type = self.paper_type_chooser.getvalue()
    if type == _('Custom'):
      type = 'custom'
    st.paper_type = type
    # orientation
    if self.paper_orientation_chooser.getvalue() == _('Portrait'):
      self.paper_orientation = 'portrait'
    else:
      st.paper_orientation = 'landscape'
    # crop_svg
    st.paper_crop_svg = self.crop_paper_in_svg.get()
    return st

  def _apply_button_callback( self, tag):
    if self.apply_button.index( tag) != 0:
      self.apply_button2.invoke(0)
      self.apply_button2.configure( Button_state = 'normal')
    else:
      self.apply_button2.invoke(1)
      self.apply_button2.configure( Button_state = 'disabled')
