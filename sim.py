import pickle
import random

import gobject
import gtk
import gtk.glade
import pygtk

from states import STATES

class ElectionSim(object):
    def __init__(self):
        self.gladefile = 'election.glade'
        self.wTree = gtk.glade.XML(self.gladefile, 'mainWindow')
        
        self.wTree.signal_autoconnect(self)
        self.wTree.get_widget('mainWindow').set_icon_from_file('obama.gif')
        self.init_widgets()
        self.update_projection()
    
    def init_widgets(self):
        self.state_table = self.wTree.get_widget('state_table')
        self.state_widgets = {}
        for idx, (norm, (name, votes)) in enumerate(STATES.iteritems()):
            table = gtk.Table(2, 2)
            table.set_name('%s_table' % norm)
            table.attach(gtk.Label('%s:' % name), 0, 1, 0, 1)
            slider = gtk.HScale(gtk.Adjustment(value=50, upper=100))
            slider.set_name('%s_scale' % norm)
            slider.set_draw_value(False)
            slider.connect('value-changed', self.slider_moved)
            sub_table = gtk.Table(2, 2)
            obama_box = gtk.CheckButton(label='Obama')
            obama_box.set_name('%s_obama' % norm)
            obama_box.connect('toggled', self.winner_determined)
            obama_label = gtk.Label('50%')
            obama_label.set_name('%s_obama_percent' % norm)
            mccain_box = gtk.CheckButton(label='McCain')
            mccain_box.set_name('%s_mccain' % norm)
            mccain_box.connect('toggled', self.winner_determined)
            mccain_label = gtk.Label('50%')
            mccain_label.set_name('%s_mccain_percent' % norm)
            sub_table.attach(obama_box, 0, 1, 0, 1)
            sub_table.attach(obama_label, 1, 2, 0, 1)
            sub_table.attach(mccain_box, 0, 1, 1, 2)
            sub_table.attach(mccain_label, 1, 2, 1, 2)
            table.attach(sub_table, 1, 2, 1, 2)
            table.attach(slider, 1, 2, 0, 1)
            self.state_widgets[norm] = (slider, obama_box, obama_label, mccain_box, mccain_label)
            self.state_table.attach(table, idx/10, idx/10+1, idx % 10, idx % 10 + 1)
        self.state_table.show_all()
    
    def slider_moved(self, widget):
        self.update_projection()
        name = '_'.join(widget.get_name().rsplit('_')[:-1])
        self.state_widgets[name][2].set_text('%s%%' % int(widget.get_value()))
        self.state_widgets[name][4].set_text('%s%%' % int(100-widget.get_value()))
    
    def update_projection(self):
        obama_votes = 0
        for i in xrange(1000):
            for slider, obama_box, obama_label, mccain_box, mccain_label in self.state_widgets.itervalues():
                name = '_'.join(slider.get_name().rsplit('_')[:-1])
                val = slider.get_value()
                votes = STATES[name][1]
                if val > random.uniform(0, 100):
                    obama_votes += votes
        obama_votes = int(obama_votes / 1000)
        self.wTree.get_widget('obama_count').set_text(str(obama_votes))
        self.wTree.get_widget('mccain_count').set_text(str(538-obama_votes))
    
    def winner_determined(self, widget):
        name = '_'.join(widget.get_name().rsplit('_')[:-1])
        winner = widget.get_name().rsplit('_')[-1]
        if widget.get_active():
            if winner == 'obama':
                idx = 3
                value = 100
            else:
                idx = 1
                value = 0
            self.state_widgets[name][idx].set_sensitive(False)
            self.state_widgets[name][0].set_value(value)
            self.state_widgets[name][0].set_sensitive(False)
        else:
            if winner == 'obama':
                idx = 3
            else:
                idx = 1
            self.state_widgets[name][idx].set_sensitive(True)
            self.state_widgets[name][0].set_value(50)
            self.state_widgets[name][0].set_sensitive(True)
    
    def save(self, widget):
        data = {}
        for slider, obama_box, obama_label, mccain_box, mccain_label in self.state_widgets.itervalues():
            name = '_'.join(slider.get_name().rsplit('_')[:-1])
            data[name] = (slider.get_value(), obama_box.get_active(), mccain_box.get_active())
        pickle.dump(data, open('data.txt', 'w'))
    
    def load(self, widget):
        data = pickle.load(open('data.txt'))
        for name, (value, obama, mccain) in data.iteritems():
            self.state_widgets[name][0].set_value(value)
            self.state_widgets[name][1].set_active(obama)
            self.state_widgets[name][3].set_active(mccain)
    
    def quit(self, *args, **kwargs):
        gtk.main_quit()

def main():
    app = ElectionSim()
    gtk.main()

if __name__ == '__main__':
    main()