import guidata
_app=guidata.qapplication() # not required if a QApplication has already been created

import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di

class Processing(dt.DataSet):
    """Example"""
    a = di.FloatItem("Parameter #1", default=2.3)
    b = di.IntItem("Parameter #2", min=0, max=10, default=5)
    aa = di.FloatItem("Parameter #1", default=2.3)
    ab = di.IntItem("Parameter #2", min=0, max=10, default=5)
    ba = di.FloatItem("Parameter #1", default=2.3)
    bb = di.IntItem("Parameter #2", min=0, max=10, default=5)
    ca = di.FloatItem("Parameter #1", default=2.3)
    cb = di.IntItem("Parameter #2", min=0, max=10, default=5)
    da = di.FloatItem("Parameter #1", default=2.3)
    db = di.IntItem("Parameter #2", min=0, max=10, default=5)
    ea = di.FloatItem("Parameter #1", default=2.3)
    eb = di.IntItem("Parameter #2", min=0, max=10, default=5)
    fa = di.FloatItem("Parameter #1", default=2.3)
    fb = di.IntItem("Parameter #2", min=0, max=10, default=5)
    ha = di.FloatItem("Parameter #1", default=2.3)
    hb = di.IntItem("Parameter #2", min=0, max=10, default=5)
    ia = di.FloatItem("Parameter #1", default=2.3)
    ib = di.IntItem("Parameter #2", min=0, max=10, default=5)

    type = di.ChoiceItem("Processing algorithm",
                         ("type 1", "type 2", "type 3"))

param = Processing()
param.edit()