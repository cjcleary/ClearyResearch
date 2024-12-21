import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import seaborn as sns
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog, QInputDialog, QMessageBox) 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from scipy.integrate import (cumulative_trapezoid as int_cumtrapz, trapezoid as int_trapz)
import qdarktheme
from win32api import GetSystemMetrics


##### defining global constants
custom_theme = {"axes.spines.right": False, "axes.spines.top": False,
                "axes.titlelocation": "left", "axes.titley": 1,
                "font.weight":"bold", "axes.titlesize": "x-large", "axes.labelsize": "x-large",
                "axes.titleweight": "bold", "axes.labelweight": 'bold'}

plt.rcParams.update({
    **custom_theme,
    'figure.facecolor': 'none',  # transparent background for plots
    'axes.labelcolor': '#ffffff',   # White axes labels
    'axes.edgecolor': '#ffffff',    # White axes edge color
    'xtick.color': '#ffffff',       # White x-axis tick labels
    'ytick.color': '#ffffff',       # white y-axis tick labels
    "axes.titlecolor": "white"    # white title label
})

# define style sheet for hte table
TABLE_STYLE =  """
QTableWidget {
    background-color: transparent;
    border: 2px solid grey; /* Adjust table border thickness and color */
    border-radius: 5px; /* Optional: Add rounded corners */
    spacing: 0.25px;
}
QTableWidget::item {
    padding: 1px; /* Optional: Add padding to table items */
    }
QHeaderView::section {
    border: none; /* Remove border from header sections */
    }
QScrollBar:horizontal, QScrollBar:vertical {
    border: none; /* Remove border from scrollbars */
    }
"""

## global constants
# dictionary for single leg jump variables
singleplate_slj_vars_dict = { 
    "bodymass": "Body Mass (kg)", 
    "jh_cm": "Jump Height (cm)", 
    "mrsi": "Modified Reactive Strength Index (AU)",
    "con_peak_power": "Concentric Peak Power (W)", 
    "ecc_peak_power": "Eccentric Peak Power (W)",
    "land_peak_power": "Landing Peak Power (W)",
    "con_mean_power":"Concentric Mean Power (W)",
    "ecc_mean_power": "Eccentric Mean Power (W)",
    "land_mean_power": "Landing Mean Power (W)", 
    "con_peak_force_n": "Concentric Peak Force (N)", 
    "con_peak_force_nkg": 'Concentric Peak Force (N\u2022kg\u207B\u00B9)',
    "ecc_peak_force_n": "Eccentric Peak Force (N)",
    "ecc_peak_force_nkg": "Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "con_mean_force_n": "Concentric Mean Force (N)",
    "con_mean_force_nkg": "Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "ecc_mean_force_n": "Eccentric Mean Force (N)",
    "ecc_mean_force_nkg": "Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "land_peak_force_n": "Landing Peak Force (N)",
    "land_peak_force_nkg": "Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "land_mean_force_n": "Landing Mean Force (N)",
    "land_mean_force_nkg": "Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "con_impulse": "Concentric Impulse (Ns)",
    "ecc_impulse": "Eccentric Impulse (Ns)",
    "positive_impulse": "Positive Impulse (Ns)",
    "land_impulse": "Landing Impulse (Ns)",
    "con_rfd": "Concentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "ecc_rfd": "Eccentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "land_rfd": "Landing Rate of Force Development (N\u2022s\u207B\u00B9)",
    "unweigh_dur": "Unweighing Phase Duration (s)",
    "ecc_time_s": "Eccentric Phase Duration (s)",
    "con_time_s": "Concentric Phase Duration (s)",
    "contraction_time_s": "Contraction Duration (s)",
    "flight_time_s": "Flight Time (s)",
    "land_time_s": "Landing Phase Duration (s)",
    "con_peak_velocity": "Concentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "ecc_peak_velocity": "Eccentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_peak_velocity": "Landing Peak Velocity (m\u2022s\u207B\u00B9)",
    "con_mean_velocity": "Concentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "ecc_mean_velocity": "Eccentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "vto": "Takeoff Velocity (m\u2022s\u207B\u00B9)",  
    "cm_depth": "Countermovement depth (cm)"      
}

# single plate drop landing vars dictionary
singleplate_droplanding_vars_dict = {
    "bodymass": "Body Mass (kg)",
    "peak_fz_total": "Peak Landing Force (N)",
    "peak_fz_rel_total": "Peak Landing Force (N\u2022kg\u207B\u00B9)",
    "loading_rate": "Loading Rate (BW/s)"
}

# single plate drop jump vars dictionary
singleplate_dropjump_vars_dict = {
    "bodymass": "Body Mass (kg)",
    "box_height": "Box Height (cm)",
    "jh_cm": "Jump Height (cm)",
    "rsi": "Reactive Strength Index (AU)",
    "con_peak_power": "Concentric Peak Power (W)",
    "ecc_peak_power": "Eccentric Peak Power (W)",
    "land_peak_power": "Landing Peak Power (W)",
    "con_mean_power": "Concentric Mean Power (W)",
    "ecc_mean_power": "Eccentric Mean Power (W)",
    "land_mean_power": "Landing Mean Power (W)",
    "con_peak_force_n": "Total Concentric Peak Force (N)",
    "con_peak_force_nkg": "Total Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "ecc_peak_force_n": "Total Eccentric Peak Force (N)",
    "ecc_peak_force_nkg": "Total Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "con_mean_force_n": "Total Concentric Mean Force (N)",
    "con_mean_force_nkg": "Total Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "ecc_mean_force_n": "Total Eccentric Mean Force (N)",
    "ecc_mean_force_nkg": "Total Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "land_peak_force_n": "Total Landing Peak Force (N)",
    "land_peak_force_nkg": "Total Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "land_mean_force_n": "Total Landing Mean Force (N)",
    "land_mean_force_nkg": "Total Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "con_impulse": "Total Concentric Impulse (Ns)",
    "ecc_impulse": "Total Eccentric Impulse (Ns)",
    "positive_impulse": "Total Positive Impulse (Ns)",
    "land_impulse": "Total Landing Impulse (Ns)",
    "groundcontact_time_s": "Ground Contact Phase Duration (s)",
    "ecc_time_s": "Eccentric Phase Duration (s)",
    "con_time_s": "Concentric Phase Duration (s)",
    "flight_time_s": "Flight Time (s)",
    "land_time_s": "Landing Phase Duration (s)",
    "con_peak_velocity": "Concentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_peak_velocity": "Landing Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_mean_velocity": "Landing Mean Velocity (m\u2022s\u207B\u00B9)",
    "con_mean_velocity": "Concentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "ecc_mean_velocity": "Eccentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "vto": "Takeoff Velocity (m\u2022s\u207B\u00B9)",   
}


# single plate CMJ vars dictionary
singleplate_cmj_vars_dict = {
    "bodymass": "Body Mass (kg)", 
    "jh_cm": "Jump Height (cm)", 
    "mrsi": "Modified Reactive Strength Index (AU)",
    "con_peak_power": "Concentric Peak Power (W)", # start of total variables
    "ecc_peak_power": "Eccentric Peak Power (W)",
    "land_peak_power": "Landing Peak Power (W)",
    "con_mean_power":"Concentric Mean Power (W)",
    "ecc_mean_power": "Eccentric Mean Power (W)",
    "land_mean_power": "Landing Mean Power (W)", 
    "con_peak_force_n": "Concentric Peak Force (N)", 
    "con_peak_force_nkg": "Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "ecc_peak_force_n": "Eccentric Peak Force (N)",
    "ecc_peak_force_nkg": "Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "con_mean_force_n": "Concentric Mean Force (N)",
    "con_mean_force_nkg": "Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "ecc_mean_force_n": "Eccentric Mean Force (N)",
    "ecc_mean_force_nkg": "Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "land_peak_force_n": "Landing Peak Force (N)",
    "land_peak_force_nkg": "Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "land_mean_force_n": "Landing Mean Force (N)",
    "land_mean_force_nkg": "Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "con_impulse": "Concentric Impulse (Ns)",
    "ecc_impulse": "Eccentric Impulse (Ns)",
    "positive_impulse": "Positive Impulse (Ns)",
    "land_impulse": "Landing Impulse (Ns)",
    "con_rfd": "Concentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "ecc_rfd": "Eccentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "land_rfd": "Landing Rate of Force Development (N\u2022s\u207B\u00B9)",
    "unweigh_dur": "Unweighing Phase Duration (s)",
    "ecc_time_s": "Eccentric Phase Duration (s)",
    "con_time_s": "Concentric Phase Duration (s)",
    "contraction_time_s": "Contraction Duration (s)",
    "flight_time_s": "Flight Time (s)",
    "land_time_s": "Landing Phase Duration (s)",
    "con_peak_velocity": "Concentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "ecc_peak_velocity": "Eccentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_peak_velocity": "Landing Peak Velocity (m\u2022s\u207B\u00B9)",
    "con_mean_velocity": "Concentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "ecc_mean_velocity": "Eccentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "vto": "Takeoff Velocity (m\u2022s\u207B\u00B9)",  
    "cm_depth": "Countermovement depth (cm)"      
}

# Double Plate Vars
dualplate_cmj_vars_dict = {
    "bodymass": "Body Mass (kg)", 
    "jh_cm": "Jump Height (cm)", 
    "mrsi": "Modified Reactive Strength Index (AU)",
    "con_peak_power": "Concentric Peak Power (W)", # start of total variables
    "ecc_peak_power": "Eccentric Peak Power (W)",
    "land_peak_power": "Landing Peak Power (W)",
    "con_mean_power":"Concentric Mean Power (W)",
    "ecc_mean_power": "Eccentric Mean Power (W)",
    "land_mean_power": "Landing Mean Power (W)", 
    "total_con_peak_force_n": "Total Concentric Peak Force (N)", 
    "total_con_peak_force_nkg": "Total Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "total_ecc_peak_force_n": "Total Eccentric Peak Force (N)",
    "total_ecc_peak_force_nkg": "Total Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "total_con_mean_force_n": "Total Concentric Mean Force (N)",
    "total_con_mean_force_nkg": "Total Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "total_ecc_mean_force_n": "Total Eccentric Mean Force (N)",
    "total_ecc_mean_force_nkg": "Total Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "total_land_peak_force_n": "Total Landing Peak Force (N)",
    "total_land_peak_force_nkg": "Total Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "total_land_mean_force_n": "Total Landing Mean Force (N)",
    "total_land_mean_force_nkg": "Total Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "total_con_impulse": "Total Concentric Impulse (Ns)",
    "total_ecc_impulse": "Total Eccentric Impulse (Ns)",
    "total_positive_impulse": "Total Positive Impulse (Ns)",
    "total_land_impulse": "Total Landing Impulse (Ns)",
    "total_con_rfd": "Total Concentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "total_ecc_rfd": "Total Eccentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "total_land_rfd": "Total Landing Rate of Force Development (N\u2022s\u207B\u00B9)",
    "left_con_peak_force_n": "Left Concentric Peak Force (N)", # start of left leg variables 
    "left_con_peak_force_nkg": "Left Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "left_ecc_peak_force_n": "Left Eccentric Peak Force (N)",
    "left_ecc_peak_force_nkg": "Left Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "left_con_mean_force_n": "Left Concentric Mean Force (N)",
    "left_con_mean_force_nkg": "Left Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "left_ecc_mean_force_n": "Left Eccentric Mean Force (N)",
    "left_ecc_mean_force_nkg": "Left Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "left_land_peak_force_n": "Left Landing Peak Force (N)",
    "left_land_peak_force_nkg": "Left Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "left_land_mean_force_n": "Left Landing Mean Force (N)",
    "left_land_mean_force_nkg": "Left Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "left_con_impulse": "Left Concentric Impulse (Ns)",
    "left_ecc_impulse":"Left Eccentric Impulse (Ns)",
    "left_positive_impulse": "Left Positive Impulse (Ns)",
    "left_land_impulse": "Left Landing Impulse (Ns)",
    "left_con_rfd": "Left Concentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "left_ecc_rfd": "Left Eccentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "left_land_rfd": "Left Landing Rate of Force Development (N\u2022s\u207B\u00B9)",
    "right_con_peak_force_n": "Right Concentric Peak Force (N)", # start of right leg variables 
    "right_con_peak_force_nkg": "Right Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "right_ecc_peak_force_n": "Right Eccentric Peak Force (N)",
    "right_ecc_peak_force_nkg": "Right Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "right_con_mean_force_n": "Right Concentric Mean Force (N)",
    "right_con_mean_force_nkg": "Right Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "right_ecc_mean_force_n": "Right Eccentric Mean Force (N)",
    "right_ecc_mean_force_nkg": "Right Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "right_land_peak_force_n": "Right Landing Peak Force (N)",
    "right_land_peak_force_nkg": "Right Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "right_land_mean_force_n": "Right Landing Mean Force (N)",
    "right_land_mean_force_nkg": "Right Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "right_con_impulse": "Right Concentric Impulse (Ns)",
    "right_ecc_impulse": "Right Eccentric Impulse (Ns)",
    "right_positive_impulse": "Right Positive Impulse (Ns)",
    "right_land_impulse": "Right Landing Impulse (Ns)",
    "right_con_rfd": "Right Concentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "right_ecc_rfd": "Right Eccentric Rate of Force Development (N\u2022s\u207B\u00B9)",
    "right_land_rfd": "Right Landing Rate of Force Development (N\u2022s\u207B\u00B9)",
    "unweigh_dur": "Unweighing Phase Duration (s)",
    "ecc_time_s": "Eccentric Phase Duration (s)",
    "con_time_s": "Concentric Phase Duration (s)",
    "contraction_time_s": "Contraction Duration (s)",
    "flight_time_s": "Flight Time (s)",
    "land_time_s": "Landing Phase Duration (s)",
    "con_peak_velocity": "Concentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "ecc_peak_velocity": "Eccentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_peak_velocity": "Landing Peak Velocity (m\u2022s\u207B\u00B9)",
    "con_mean_velocity": "Concentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "ecc_mean_velocity": "Eccentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "vto": "Takeoff Velocity (m\u2022s\u207B\u00B9)",  
    "cm_depth": "Countermovement depth (cm)"      
}

# dual plate drop landing vars dictionary
dualplate_droplanding_vars_dict = {
    "bodymass": "Body Mass (kg)",
    "total_peak_force_n": "Total Peak Landing Force (N)",
    "total_peak_force_nkg": "Total Peak Landing Force (N\u2022kg\u207B\u00B9)",
    "left_peak_force_n": "Left Peak Landing Force (N)",
    "left_peak_force_nkg": "Left Peak Landing Force (N\u2022kg\u207B\u00B9)",
    "right_peak_force_n": "Right Peak Landing Force (N)",
    "right_peak_force_nkg": "Right Peak Landing Force (N\u2022kg\u207B\u00B9)",
    "total_loading_rate_bw_s": "Total Loading Rate (BW/s)",
    "left_loading_rate_bw_s": "Left Loading Rate (BW/s)",
    "right_loading_rate_bw_s": "Right Loading Rate (BW/s)",
}

# dual plate drop jump vars
dualplate_dropjump_vars_dict = {
    "bodymass": "Body Mass (kg)",
    "box_height": "Box Height (cm)",
    "jh_cm": "Jump Height (cm)",
    "rsi": "Reactive Strength Index (AU)",
    "con_peak_power": "Concentric Peak Power (W)",
    "ecc_peak_power": "Eccentric Peak Power (W)",
    "land_peak_power": "Landing Peak Power (W)",
    "con_mean_power": "Concentric Mean Power (W)",
    "ecc_mean_power": "Eccentric Mean Power (W)",
    "land_mean_power": "Landing Mean Power (W)",
    "total_con_peak_force_n": "Total Concentric Peak Force (N)",
    "total_con_peak_force_nkg": "Total Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "total_ecc_peak_force_n": "Total Eccentric Peak Force (N)",
    "total_ecc_peak_force_nkg": "Total Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "total_con_mean_force_n": "Total Concentric Mean Force (N)",
    "total_con_mean_force_nkg": "Total Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "total_ecc_mean_force_n": "Total Eccentric Mean Force (N)",
    "total_ecc_mean_force_nkg": "Total Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "total_land_peak_force_n": "Total Landing Peak Force (N)",
    "total_land_peak_force_nkg": "Total Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "total_land_mean_force_n": "Total Landing Mean Force (N)",
    "total_land_mean_force_nkg": "Total Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "total_con_impulse": "Total Concentric Impulse (Ns)",
    "total_ecc_impulse": "Total Eccentric Impulse (Ns)",
    "total_positive_impulse": "Total Positive Impulse (Ns)",
    "total_land_impulse": "Total Landing Impulse (Ns)",
    "left_con_peak_force_n": "Left Concentric Peak Force (N)", # start of left leg variables 
    "left_con_peak_force_nkg": "Left Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "left_ecc_peak_force_n": "Left Eccentric Peak Force (N)",
    "left_ecc_peak_force_nkg": "Left Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "left_con_mean_force_n": "Left Concentric Mean Force (N)",
    "left_con_mean_force_nkg": "Left Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "left_ecc_mean_force_n": "Left Eccentric Mean Force (N)",
    "left_ecc_mean_force_nkg": "Left Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "left_land_peak_force_n": "Left Landing Peak Force (N)",
    "left_land_peak_force_nkg": "Left Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "left_land_mean_force_n": "Left Landing Mean Force (N)",
    "left_land_mean_force_nkg": "Left Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "left_con_impulse": "Left Concentric Impulse (Ns)",
    "left_ecc_impulse":"Left Eccentric Impulse (Ns)",
    "left_positive_impulse": "Left Positive Impulse (Ns)",
    "left_land_impulse": "Left Landing Impulse (Ns)",
    "right_con_peak_force_n": "Right Concentric Peak Force (N)", # start of right leg variables 
    "right_con_peak_force_nkg": "Right Concentric Peak Force (N\u2022kg\u207B\u00B9)",
    "right_ecc_peak_force_n": "Right Eccentric Peak Force (N)",
    "right_ecc_peak_force_nkg": "Right Eccentric Peak Force (N\u2022kg\u207B\u00B9)",
    "right_con_mean_force_n": "Right Concentric Mean Force (N)",
    "right_con_mean_force_nkg": "Right Concentric Mean Force (N\u2022kg\u207B\u00B9)",
    "right_ecc_mean_force_n": "Right Eccentric Mean Force (N)",
    "right_ecc_mean_force_nkg": "Right Eccentric Mean Force (N\u2022kg\u207B\u00B9)",
    "right_land_peak_force_n": "Right Landing Peak Force (N)",
    "right_land_peak_force_nkg": "Right Landing Peak Force (N\u2022kg\u207B\u00B9)",
    "right_land_mean_force_n": "Right Landing Mean Force (N)",
    "right_land_mean_force_nkg": "Right Landing Mean Force (N\u2022kg\u207B\u00B9)",
    "right_con_impulse": "Right Concentric Impulse (Ns)",
    "right_ecc_impulse": "Right Eccentric Impulse (Ns)",
    "right_positive_impulse": "Right Positive Impulse (Ns)",
    "right_land_impulse": "Right Landing Impulse (Ns)",
    "groundcontact_time_s": "Ground Contact Phase Duration (s)",
    "ecc_time_s": "Eccentric Phase Duration (s)",
    "con_time_s": "Concentric Phase Duration (s)",
    "flight_time_s": "Flight Time (s)",
    "land_time_s": "Landing Phase Duration (s)",
    "con_peak_velocity": "Concentric Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_peak_velocity": "Landing Peak Velocity (m\u2022s\u207B\u00B9)",
    "land_mean_velocity": "Landing Mean Velocity (m\u2022s\u207B\u00B9)",
    "con_mean_velocity": "Concentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "ecc_mean_velocity": "Eccentric Mean Velocity (m\u2022s\u207B\u00B9)",
    "vto": "Takeoff Velocity (m\u2022s\u207B\u00B9)",   
}


##### Start of analysis functions, first SLJ
class SinglePlateSLJAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        # File dictionary to enable handling of multiple files
        self.file_path_dict = {}
        self.current_file_left = None
        self.current_file_right = None
        self.table_dat = pd.DataFrame()
        
        # Initialize dataframes 
        self.outcome_dat =  pd.DataFrame({'Variable': singleplate_slj_vars_dict.values()})
        self.selected_vars = []
        
        # Display the default table (outcome_dat)
        self.display_table(self.table_dat)
        self.left_drop_count = 0
        self.right_drop_count = 0
        
         # Initialize the VariableSelectionDialog with the data dictionary
        self.slj_vars_dict = singleplate_slj_vars_dict
              
    def initUI(self):
        self.setWindowTitle("SLJ Analysis")
        self.setGeometry(100, 100, 1600, 800)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout()  # for plots
        self.rightLayout = QVBoxLayout()  # for table
     
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2) 
        
        # Create a dropdown box for selecting files for the left plot
        self.fileComboBoxLeft = QComboBox()
        self.fileComboBoxLeft.currentIndexChanged.connect(self.on_file_combobox_left_changed)
        self.leftLayout.addWidget(self.fileComboBoxLeft)

        # Label for left plot file selection
        self.label1 = QLabel("Drag and Drop Left Leg Trial(s) here:", self)
        self.label1.setFont(QFont("Arial bold", 10))
        self.label1.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label1)

        # First plot (Left)
        self.figure1 = plt.Figure(figsize=(12, 10))
        self.canvas1 = FigureCanvas(self.figure1)
        self.leftLayout.addWidget(self.canvas1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self, coordinates = False)
        self.leftLayout.addWidget(self.toolbar1)

        # Create a dropdown box for selecting files for the right plot
        self.fileComboBoxRight = QComboBox()
        self.fileComboBoxRight.currentIndexChanged.connect(self.on_file_combobox_right_changed)
        self.leftLayout.addWidget(self.fileComboBoxRight)
        
        # Label for right plot file selection
        self.label2 = QLabel("Drag and Drop Right Leg Trial(s) here:", self)
        self.label2.setFont(QFont("Arial bold", 10))
        self.label2.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label2)

        # Second plot (Right)
        self.figure2 = plt.Figure(figsize=(12, 10))
        self.canvas2 = FigureCanvas(self.figure2)
        self.leftLayout.addWidget(self.canvas2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self, coordinates = False)
        self.leftLayout.addWidget(self.toolbar2)
        
        # defining the table for values
        # Create a QComboBox for selecting data displayed in table
        self.comboBox = QComboBox()
        self.comboBox.addItems(['Full Results', "Average Results"])
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.rightLayout.addWidget(self.comboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)   
            
        # Adding in buttons
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # Add export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
                     
        # Quit program button       
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton) 
        self.setAcceptDrops(True)
        
        # Home button
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returntoHome)
        self.buttonLayout.addWidget(self.homeButton)
               
        self.topLayout.addLayout(self.buttonLayout)
        
        # Column selection for safety of making sure
        self.columnSelectionPrompt()   
        
    # Define column selection prompt page
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        
        self.fz_col, ok1 = QInputDialog.getItem(self, "Select Column", "Select 'Fz' Column from Excel file, double check this prior \nto any analyses or the program will not run:", columnOptions, 5, False)
            
        if ok1:
            self.fz_col = ord(self.fz_col) - 65
        else:
            self.close()
    
     # Method to update the table display       
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        # Font settings for table
        variable_font = QFont()
        variable_font.setBold(True)
        variable_font.setFamily("Arial")
        variable_font.setPointSize(8) 
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(8)
     
        # Loop through the dataframe to populate the table
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i, j]
                if j == 0:  # First column (strings)
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:  # Second and subsequent columns (floats)
                    numeric_value = float(value)
                    item = QTableWidgetItem(f"{numeric_value:.2f}")
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i, j, item)

        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
        
    # Update the on_combobox_changed method to handle three dataframes this needs to be modifed
    def on_combobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.display_table(self.average_dat)  
    
    # Dropdown (Left) changed method
    def on_file_combobox_left_changed(self):
        file_key = self.fileComboBoxLeft.currentText()
        self.current_file_left = self.file_path_dict[file_key]
        self.processSLJFile(self.current_file_left)

    # Dropdown (Right) changed method
    def on_file_combobox_right_changed(self):
        file_key = self.fileComboBoxRight.currentText()
        self.current_file_right = self.file_path_dict[file_key]
        self.processSLJFile(self.current_file_right)

    # For dragging in new files        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
                
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]  # Remove .csv extension
                self.file_path_dict[file_name] = file_path
                
                if 'LEFT' in file_name.upper():
                    if self.fileComboBoxLeft.findText(file_name) == -1:
                        self.fileComboBoxLeft.addItem(file_name)
                    self.fileComboBoxLeft.setCurrentText(file_name)
                    self.current_file_left = file_path
                    self.on_file_combobox_left_changed()
                    self.left_drop_count = self.left_drop_count + 1
                    self.processSLJFile(file_path)
                    self.average_data(self.outcome_dat)

                if 'RIGHT' in file_name.upper():
                    if self.fileComboBoxRight.findText(file_name) == -1:
                        self.fileComboBoxRight.addItem(file_name)
                    self.right_drop_count = self.right_drop_count + 1
                    self.fileComboBoxRight.setCurrentText(file_name)
                    self.current_file_right = file_path
                    self.on_file_combobox_right_changed()
                    self.processSLJFile(file_path)
                    self.average_data(self.outcome_dat)

    # Process the SLJ file(s) 
    def processSLJFile(self, file_path):
        outcome_dat = self.outcome_dat
        file_name = os.path.basename(file_path)[:-4]
        
        if 'LEFT' in file_name.upper():
            self.jump_leg_name = 'LEFT'
        if 'RIGHT' in file_name.upper():
            self.jump_leg_name = 'RIGHT'

        dat = pd.read_csv(file_path)
        
        fz_jump_leg = dat.iloc[:, self.fz_col]
        fz_total = fz_jump_leg
        
        # would prefer for this to be a whole 1-3 seconds. 
        bw_mean = fz_total[0:1500].mean()
        bw_sd = fz_total[0:1500].std()
        body_mass = bw_mean / 9.81
        
        # calculate time
        sf = 1000
        dat_len = len(fz_jump_leg)
        trial_time = dat_len / sf
        time_s = np.linspace(start = 0, stop = trial_time, num = dat_len)
        
        # calculate other arrays
        accel = (fz_total - bw_mean) / body_mass
        velo = int_cumtrapz(x = time_s, y = accel) 
        position = int_cumtrapz(x = time_s[1:], y = velo)
        power = fz_jump_leg[1:] * velo

        start_move = 20
        while fz_jump_leg[start_move] > (bw_mean - (bw_sd  * 5)):
            start_move = start_move + 1
        while fz_total[start_move] < bw_mean:
                start_move = start_move - 1
            
        takeoff = start_move 
        while fz_jump_leg[takeoff] > 30:
            takeoff = takeoff + 1
            
        start_ecc_velo = min(velo[start_move:takeoff])
        start_ecc = list(velo).index(start_ecc_velo)
        
        start_con = start_ecc
        while velo[start_con] < 0:
            start_con = start_con + 1    
            
        land = takeoff + 150
        while fz_jump_leg[land] < 30:
            land = land + 1
            
        end_land = land + 100
        while fz_jump_leg[end_land] > bw_mean:
            end_land = end_land + 1
        while fz_jump_leg[end_land] < bw_mean:
            end_land = end_land - 1        
            
        ### Make arrays for each phase - force
        unweigh_fz = fz_jump_leg[start_move:start_ecc]
        ecc_fz = fz_jump_leg[start_ecc:start_con]
        con_fz = fz_jump_leg[start_con:takeoff]
        land_fz = fz_jump_leg[land:end_land]
        positive_fz = fz_jump_leg[start_ecc:takeoff]
        
        ### - velo
        unweigh_velo = velo[start_move:start_ecc]
        ecc_velo = velo[start_ecc:start_con]
        con_velo = velo[start_con:takeoff]
        land_velo = velo[land:end_land]
                
        ### - power 
        ecc_power = power[start_ecc:start_con]
        con_power = power[start_con:takeoff]
        land_power = power[land:end_land]
                
        ##### Power outcomes 
        ecc_peak_power = ecc_power.min()
        ecc_mean_power = ecc_power.mean()
        con_peak_power = con_power.max()
        con_mean_power = con_power.mean()
        land_peak_power = land_power.max()
        land_mean_power = land_power.mean()
        
        ##### Kinetic phase-specific outcome variables
        ### TOTAL kinetic phase outcome variables
        # eccentric
        ecc_fz_peak_force_n = ecc_fz.max()
        ecc_fz_peak_force_nkg = ecc_fz_peak_force_n/body_mass
        ecc_fz_mean_force_n = ecc_fz.mean()
        ecc_fz_mean_force_nkg = ecc_fz_mean_force_n/body_mass
        ecc_fz_imp = int_trapz(ecc_fz)/sf
                
        # concentric
        con_fz_peak_force_n = con_fz.max()
        con_fz_peak_force_nkg = con_fz_peak_force_n/body_mass
        con_fz_mean_force_n = con_fz.mean()
        con_fz_mean_force_nkg = con_fz_mean_force_n/body_mass
        con_fz_imp = int_trapz(con_fz)/sf
                
        # positve impulse
        positive_imp = int_trapz(positive_fz)/sf
            
        # landing
        land_fz_peak_force_n = land_fz.max()
        land_fz_peak_force_nkg = land_fz_peak_force_n/body_mass
        land_fz_mean_force_n = land_fz.mean()
        land_fz_mean_force_nkg = land_fz_mean_force_n/body_mass
        land_fz_imp = int_trapz(land_fz)/sf   
                
        ##### Time specific outcomes
        unweigh_time_s = time_s[start_ecc] - time_s[start_move]
        contraction_time_s = time_s[takeoff] - time_s[start_move]
        ecc_time_s = time_s[start_con] - time_s[start_ecc]
        con_time_s = time_s[takeoff] - time_s[start_con]
        flight_time_s = time_s[land] - time_s[takeoff]
        land_time_s = time_s[end_land] - time_s[land]        
                
        ##### RFD outcomes
        ecc_rfd = (fz_jump_leg[start_con] - fz_jump_leg[start_ecc]) / ecc_time_s
        con_rfd = (fz_jump_leg[start_con] - fz_jump_leg[takeoff]) / con_time_s
        land_rfd = (fz_jump_leg[end_land] - fz_jump_leg[land]) / land_time_s
            
        ##### Velocity outcomes
        ecc_peak_velo = ecc_velo.min()
        con_peak_velo = con_velo.max()
        ecc_mean_velo = ecc_velo.mean()
        con_mean_velo = con_velo.mean()
        land_peak_velo = land_velo.min()
                                
        ##### Outcome variables
        vto = velo[takeoff]
        jh = ((vto ** 2)/(9.81 * 2))
        jh_cm = jh * 100
        mrsi = jh/contraction_time_s
        depth = position[start_move:takeoff].min()
        depth_cm = depth * 100
            
        # combine into a list
        values_dat = [body_mass, jh_cm, mrsi, con_peak_power,
                    ecc_peak_power,land_peak_power, con_mean_power, ecc_mean_power,
                    land_mean_power, con_fz_peak_force_n, con_fz_peak_force_nkg, ecc_fz_peak_force_n, 
                    ecc_fz_peak_force_nkg, con_fz_mean_force_n, con_fz_mean_force_nkg, ecc_fz_mean_force_n,
                    ecc_fz_mean_force_nkg, land_fz_peak_force_n, land_fz_peak_force_nkg, 
                    land_fz_mean_force_n, land_fz_mean_force_nkg, con_fz_imp,
                    ecc_fz_imp, positive_imp, land_fz_imp, con_rfd,
                    ecc_rfd, land_rfd, unweigh_time_s, ecc_time_s,
                    con_time_s, contraction_time_s, flight_time_s, land_time_s,
                    con_peak_velo, ecc_peak_velo, land_peak_velo, con_mean_velo,
                    ecc_mean_velo, vto, depth_cm]
        
        # round with list comprehension
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n),3) for n in values_dat]
                  
        table_vars = list(singleplate_slj_vars_dict.values())   
        
        self.table_dat = pd.DataFrame({'Variable': table_vars,
                                      file_name: values_dat_table})
        self.display_table(self.outcome_dat) # display data in table
        
        outcome_dat[file_name] = values_dat_clean 
        
        # Define time outcomes for plotting  
        start_move_s = time_s[start_move]
        start_ecc_s = time_s[start_ecc]
        start_con_s = time_s[start_con]
        takeoff_s = time_s[takeoff]
        land_s = time_s[land]
        end_land_s = time_s[end_land]
        
        # For adding annotations             
        annotations = {"Unweigh": start_move_s, 
                       "Ecentric": start_ecc_s, 
                       "Concentric": start_con_s, 
                       "Flight": takeoff_s, 
                       "Landing": land_s+0.1}
        
        if 'LEFT' in file_name.upper():
            col_jump = 'blue'
            self.figure1.clear()
            ax = self.figure1.add_subplot(111)          
            ax.axhline(y = bw_mean, color = 'black', ls = "--", lw = 0.4)
            ax.axvline(x = start_move_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = start_ecc_s, ls = ':', color = 'black', lw = 0.4)
            ax.axvline(x = start_con_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = takeoff_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = land_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = end_land_s, ls = ":", color = 'black', lw = 0.4)
            sns.lineplot(x=time_s[0:end_land+500], y=fz_jump_leg[0:end_land+500], color=col_jump, ax=ax)
            ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
            ax.set_ylabel("Force (N)")
            y_pos = ax.get_ylim()[1]*0.95
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure1.tight_layout()
            self.canvas1.draw()

        if 'RIGHT' in file_name.upper():
            col_jump = 'red'
            self.figure2.clear()
            ax = self.figure2.add_subplot(111)
            ax.axhline(y = bw_mean, color = 'black', ls = "--", lw = 0.4)
            ax.axvline(x = start_move_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = start_ecc_s, ls = ':', color = 'black', lw = 0.4)
            ax.axvline(x = start_con_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = takeoff_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = land_s, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = end_land_s, ls = ":", color = 'black', lw = 0.4)
            sns.lineplot(x=time_s[0:end_land+500], y=fz_jump_leg[0:end_land+500], color=col_jump, ax=ax)
            ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
            ax.set_ylabel("Force (N)")
            
            y_pos = ax.get_ylim()[1]*0.95
            # add annotations to force plt
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure2.tight_layout()    
            self.canvas2.draw()
            
        self.outcome_dat = outcome_dat  
    
    # average data
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        var_names = var_names[1:]
        left_columns = dataframe.loc[:, dataframe.columns.str.contains("LEFT")]
        right_columns = dataframe.loc[:, dataframe.columns.str.contains("RIGHT")]
        left_columns_mean = left_columns.mean(axis = 1)
        left_columns_mean = left_columns_mean[1:]
        left_columns_mean = left_columns_mean.round(3)
        right_columns_mean = right_columns.mean(axis = 1)
        right_columns_mean = right_columns_mean[1:]
        right_columns_mean = right_columns_mean.round(3)
        left_right_lsi = left_columns_mean/right_columns_mean
        left_right_lsi = left_right_lsi.round(3)
        right_left_lsi = right_columns_mean/left_columns_mean
        right_left_lsi = right_left_lsi.round(3)
        average_dat = pd.DataFrame({"Variable": var_names,
                                    "Left": left_columns_mean,
                                    "Right": right_columns_mean,
                                    "L/R LSI": left_right_lsi,
                                    "R/L LSI": right_left_lsi})        
        self.average_dat = average_dat
    
    # defining export data function
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        average_df = self.average_dat
        outcome_df = self.outcome_dat        
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += '.xlsx'
            with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = "Individual Data", index = False)     
    def returntoHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close() 
    def closeApp(self):
        self.close()
        
class SinglePlateSLDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
    
     # File dictionary to enable handling of multiple files
        self.file_path_dict = {}
        self.current_file_left = None
        self.current_file_right = None
        self.table_dat = pd.DataFrame()
        
        # Initialize dataframes 
        self.outcome_dat =  pd.DataFrame({'Variable': singleplate_droplanding_vars_dict.values()})
        self.selected_vars = []
        
        # get user inputs for mass and drop height
        self.get_user_inputs()
        
        # Display the default table (outcome_dat)
        self.display_table(self.table_dat)
        self.left_drop_count = 0
        self.right_drop_count = 0
        
         # Initialize the VariableSelectionDialog with the data dictionary
        self.sldrop_vars_dict = singleplate_droplanding_vars_dict
       
    def initUI(self):
        self.setWindowTitle("Single Plate Drop Landing Analysis")
        self.setGeometry(100, 100, 1600, 800)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout()  # for plots
        self.rightLayout = QVBoxLayout()  # for table
     
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2) 
        
        # Create a dropdown box for selecting files for the left plot
        self.fileComboBoxLeft = QComboBox()
        self.fileComboBoxLeft.currentIndexChanged.connect(self.on_file_combobox_left_changed)
        self.leftLayout.addWidget(self.fileComboBoxLeft)

        # Label for left plot file selection
        self.label1 = QLabel("Drag and Drop Left Leg Trial(s) here:", self)
        self.label1.setFont(QFont("Arial bold", 10))
        self.label1.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label1)

        # First plot (Left)
        self.figure1 = plt.Figure(figsize=(12, 8))
        self.canvas1 = FigureCanvas(self.figure1)
        self.leftLayout.addWidget(self.canvas1)

        # Create a dropdown box for selecting files for the right plot
        self.fileComboBoxRight = QComboBox()
        self.fileComboBoxRight.currentIndexChanged.connect(self.on_file_combobox_right_changed)
        self.leftLayout.addWidget(self.fileComboBoxRight)
        
        # Label for right plot file selection
        self.label2 = QLabel("Drag and Drop Right Leg Trial(s) here:", self)
        self.label2.setFont(QFont("Arial bold", 10))
        self.label2.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label2)

        # Second plot (Right)
        self.figure2 = plt.Figure(figsize=(12, 8))
        self.canvas2 = FigureCanvas(self.figure2)
        self.leftLayout.addWidget(self.canvas2)
        
        # defining the table for values
        # Create a QComboBox for selecting data displayed in table
        self.comboBox = QComboBox()
        self.comboBox.addItems(['Full Results', "Average Results"])
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.rightLayout.addWidget(self.comboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)   
            
        # Adding in buttons
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # Add export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
                     
        # Quit program button       
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton) 
        self.setAcceptDrops(True)
        
        # Home Button
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returntoHome)
        self.buttonLayout.addWidget(self.homeButton)
               
        self.topLayout.addLayout(self.buttonLayout)
        
        # Column selection for safety of making sure
        self.columnSelectionPrompt()
        
    def get_user_inputs(self):
        # input for participant's body mass
        pt_mass_lb, ok1 = QInputDialog.getDouble(self, "Input", "Enter Individual's Body Mass (pounds) - this MUST be accurate:", decimals=2)
        if ok1:
            pt_mass_kg = pt_mass_lb/2.2046
            self.pt_mass = pt_mass_kg
        else:
            self.close()

    # Define column selection prompt page
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_col, ok1 = QInputDialog.getItem(self, "Select Column", "Select 'Fz' Column from Excel file, double check this prior \nto any analyses or the program will not run:", columnOptions, 5, False)
        if ok1:
            self.fz_col = ord(self.fz_col) - 65
        else:
            self.close()
    
    # Method to update the table display       
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        
        # Font settings for table
        variable_font = QFont()
        variable_font.setBold(True)
        variable_font.setFamily("Arial")
        variable_font.setPointSize(8)
            
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(8)
     
        # Loop through the dataframe to populate the table
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i, j]

                if j == 0:  # First column (strings)
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:  # Second and subsequent columns (floats)
                    numeric_value = float(value)
                    item = QTableWidgetItem(f"{numeric_value:.2f}")
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                
                self.table.setItem(i, j, item)

        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
        
    # Update the on_combobox_changed method to handle three dataframes this needs to be modifed
    def on_combobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.average_data(self.outcome_dat)
            self.display_table(self.average_dat)  
    
    # Dropdown (Left) changed method
    def on_file_combobox_left_changed(self):
        file_key = self.fileComboBoxLeft.currentText()
        self.current_file_left = self.file_path_dict[file_key]
        self.processSLDropFile(self.current_file_left)

    # Dropdown (Right) changed method
    def on_file_combobox_right_changed(self):
        file_key = self.fileComboBoxRight.currentText()
        self.current_file_right = self.file_path_dict[file_key]
        self.processSLDropFile(self.current_file_right)

    # For dragging in new files        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
                
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]  # Remove .csv extension
                self.file_path_dict[file_name] = file_path
                if 'LEFT' in file_name.upper():
                    if self.fileComboBoxLeft.findText(file_name) == -1:
                        self.fileComboBoxLeft.addItem(file_name)
                    self.fileComboBoxLeft.setCurrentText(file_name)
                    self.current_file_left = file_path
                    self.on_file_combobox_left_changed()
                    self.left_drop_count = self.left_drop_count + 1 
                    self.processSLDropFile(file_path)
                    self.average_data(self.outcome_dat)   
                if 'RIGHT' in file_name.upper():
                    if self.fileComboBoxRight.findText(file_name) == -1:
                        self.fileComboBoxRight.addItem(file_name)
                    self.right_drop_count = self.right_drop_count + 1
                    self.fileComboBoxRight.setCurrentText(file_name)
                    self.current_file_right = file_path
                    self.on_file_combobox_right_changed()
                    self.right_drop_count = self.right_drop_count +1
                    self.processSLDropFile(file_path)
                    self.average_data(self.outcome_dat)
               
    # Process the SL Drop Landing file(s) 
    def processSLDropFile(self, file_path):
        # constants
        sf = 1000
        pt_mass = self.pt_mass
        pt_weight = pt_mass * 9.81
        outcome_dat = self.outcome_dat
        file_name = os.path.basename(file_path)[:-4]
        
        if 'LEFT' in file_name.upper():
            self.jump_leg_name = 'LEFT'
        if 'RIGHT' in file_name.upper():
            self.jump_leg_name = 'RIGHT'

        dat = pd.read_csv(file_path)           
        fz_landing_leg = dat.iloc[:, self.fz_col]
        fz_total = fz_landing_leg
        
        trial_len = len(fz_total)
        trial_time = trial_len/sf
        time = np.linspace(start = 0, stop = trial_time, num = trial_len)

        # determine indices
        impact = 500
        while fz_total[impact] < 30:
            impact = impact + 1 
        impact_time = time[impact]
        
        # identify peak values and their indices of time and index
        peak_fz = fz_total.max()
        peak_fz_index = fz_total.argmax(axis = 0)
        peak_fz_time = time[peak_fz_index]
        
        # peak fz relative
        peak_fz_rel = peak_fz/pt_mass
        
        # calculate time to peak Fz for loading rate
        time_to_peak_fz = peak_fz_time - impact_time
        
        # calculate force in units of N of BM
        fz_bwn = fz_total/pt_weight
        peak_fz_bwn = fz_bwn.max()
        
        # calculate loading rate
        loading_rate = peak_fz_bwn/time_to_peak_fz
        
        # combine into a list
        values_dat = [pt_mass,
                      peak_fz,
                      peak_fz_rel,
                      loading_rate]
                      #tts 
                      
        
        # round with list comprehension
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n),3) for n in values_dat]
                  
        table_vars = list(singleplate_droplanding_vars_dict.values())   
        
        self.table_dat = pd.DataFrame({'Variable': table_vars,
                                      file_name: values_dat_table})
        self.display_table(self.outcome_dat) # display data in table
        
        outcome_dat[file_name] = values_dat_clean 
        
        # Cropped arrays for plotting
        cropped_time = time[impact-250:]
        fz_cropped = fz_total[impact-250:]
        
        # For adding annotations             
        annotations = {"Impact": impact_time, 
                       "Peak Force": peak_fz_time}
        
        if 'LEFT' in file_name.upper():
            col_jump = 'blue'
            self.figure1.clear()
            ax = self.figure1.add_subplot(111)          
            ax.axvline(x = impact_time, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = peak_fz_time, ls = ':', color = 'black', lw = 0.4)
            sns.lineplot(x=cropped_time, y=fz_cropped, color=col_jump, ax=ax)
            ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
            ax.set_ylabel("Force (N)")
            y_pos = ax.get_ylim()[1]*0.95
            # add annotations to force plt
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure1.tight_layout();
            self.canvas1.draw()

        if 'RIGHT' in file_name.upper():
            col_jump = 'red'
            self.figure2.clear()
            ax = self.figure2.add_subplot(111)           
            ax.axvline(x = impact_time, ls = ":", color = 'black', lw = 0.4)
            ax.axvline(x = peak_fz_time, ls = ':', color = 'black', lw = 0.4)
            sns.lineplot(x=cropped_time, y=fz_cropped, color=col_jump, ax=ax)
            ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
            ax.set_ylabel("Force (N)")
            y_pos = ax.get_ylim()[1]*0.95
            # add annotations to force plt
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure2.tight_layout();
            self.canvas2.draw()

        self.outcome_dat = outcome_dat  
    
    # average data
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        var_names = var_names[1:]
        left_columns = dataframe.loc[:, dataframe.columns.str.contains("LEFT")]
        right_columns = dataframe.loc[:, dataframe.columns.str.contains("RIGHT")]
        left_columns_mean = left_columns.mean(axis = 1)
        left_columns_mean = left_columns_mean[1:]
        left_columns_mean = left_columns_mean.round(3)
        right_columns_mean = right_columns.mean(axis = 1)
        right_columns_mean = right_columns_mean[1:]
        right_columns_mean = right_columns_mean.round(3)
        left_right_lsi = left_columns_mean/right_columns_mean
        left_right_lsi = left_right_lsi.round(3)
        right_left_lsi = right_columns_mean/left_columns_mean
        right_left_lsi = right_left_lsi.round(3)
        average_dat = pd.DataFrame({"Variable": var_names,
                                    "Left": left_columns_mean,
                                    "Right": right_columns_mean,
                                    "L/R LSI": left_right_lsi,
                                    "R/L LSI": right_left_lsi})        
        self.average_dat = average_dat
    # defining export data function
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        average_df = self.average_dat
        outcome_df = self.outcome_dat        
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += '.xlsx'
            with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = "Individual Data", index = False)
    def returntoHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()                    
    def closeApp(self):
        self.close()
        
# single leg drop jump analysis
class SinglePlateDropJumpAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        self.file_path_dict = {}
        self.current_file_left = None
        self.current_file_right = None
        self.table_dat = pd.DataFrame()
        
        # initialize dataframes
        self.outcome_dat = pd.DataFrame({'Variable': singleplate_dropjump_vars_dict.values()})
        
        # get user inputs
        self.pt_mass = ()
        self.box_height = ()
        self.get_user_inputs()
        
        # display the default table
        self.display_table(self.table_dat)
        self.left_drop_count = 0
        self.right_drop_count = 0
        
    def initUI(self):
        self.setWindowTitle("Single Plate Drop Jump Analysis")
        self.setGeometry(100, 100, 1600, 800)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout()  # for plots
        self.rightLayout = QVBoxLayout()  # for table
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2) 
        
        # Create a dropdown box for selecting files for the left plot
        self.fileComboBoxLeft = QComboBox()
        self.fileComboBoxLeft.currentIndexChanged.connect(self.on_file_combobox_left_changed)
        self.leftLayout.addWidget(self.fileComboBoxLeft)

        # Label for left plot file selection
        self.label1 = QLabel("Drag and Drop Left Leg Trial(s) here:", self)
        self.label1.setFont(QFont("Arial bold", 10))
        self.label1.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label1)

        # First plot (Left)
        self.figure1 = plt.Figure(figsize=(12, 10))
        self.canvas1 = FigureCanvas(self.figure1)
        self.leftLayout.addWidget(self.canvas1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self, coordinates = False)
        self.leftLayout.addWidget(self.toolbar1)

        # Create a dropdown box for selecting files for the right plot
        self.fileComboBoxRight = QComboBox()
        self.fileComboBoxRight.currentIndexChanged.connect(self.on_file_combobox_right_changed)
        self.leftLayout.addWidget(self.fileComboBoxRight)
        
        # Label for right plot file selection
        self.label2 = QLabel("Drag and Drop Right Leg Trial(s) here:", self)
        self.label2.setFont(QFont("Arial bold", 10))
        self.label2.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label2)

        # Second plot (Right)
        self.figure2 = plt.Figure(figsize=(12, 10))
        self.canvas2 = FigureCanvas(self.figure2)
        self.leftLayout.addWidget(self.canvas2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self, coordinates = False)
        self.leftLayout.addWidget(self.toolbar2)

        # defining the table for values
        # Create a QComboBox for selecting data displayed in table
        self.comboBox = QComboBox()
        self.comboBox.addItems(['Full Results', "Average Results"])
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.rightLayout.addWidget(self.comboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)   
            
        # Adding in buttons
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # Add export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
                     
        # Quit program button       
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton) 
        self.setAcceptDrops(True)
        
        # Home button
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returntoHome)
        self.buttonLayout.addWidget(self.homeButton)
               
        self.topLayout.addLayout(self.buttonLayout)
        
        # Column selection for safety of making sure
        self.columnSelectionPrompt()  
    
    # custom function for user inputs
    def get_user_inputs(self):
        # input for participant's body mass
        pt_mass_lb, ok1 = QInputDialog.getDouble(self, "Input", "Enter Individual's Body Mass (pounds)- This must be accurate:", decimals = 2)
        if ok1:
            pt_mass_kg = pt_mass_lb / 2.2046
            self.pt_mass = pt_mass_kg
        else:
            self.close()
        # input for box height
        # defaults and constants    
        default_box_height_in = 16.0

        drop_height_in, ok2 = QInputDialog.getDouble(self, "Input", "Enter Box Height (inches):", decimals = 2, value = default_box_height_in)
        if ok2:
            drop_height_cm = drop_height_in * 2.54
            drop_height_m = drop_height_cm/100
            self.drop_height = drop_height_m
        else:
            self.close()
    
    # Define column selection prompt page
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_col, ok1 = QInputDialog.getItem(self, "Select Column", "Select 'Fz' Column from Excel file, double check this prior \nto any analyses or the program will not run:", columnOptions, 5, False)
        if ok1:
            self.fz_col = ord(self.fz_col) - 65
        else:
            self.close()
    
    # Method to update the table display       
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        # Font settings for table
        variable_font = QFont()
        variable_font.setBold(True)
        variable_font.setFamily("Arial")
        variable_font.setPointSize(8) 
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(8)
     
        # Loop through the dataframe to populate the table
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i, j]
                if j == 0:  # First column (strings)
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:  # Second and subsequent columns (floats)
                    numeric_value = float(value)
                    item = QTableWidgetItem(f"{numeric_value:.2f}")
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i, j, item)

        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
        
    # Update the on_combobox_changed method to handle three dataframes this needs to be modifed
    def on_combobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.display_table(self.average_dat)  
    
    # Dropdown (Left) changed method
    def on_file_combobox_left_changed(self):
        file_key = self.fileComboBoxLeft.currentText()
        self.current_file_left = self.file_path_dict[file_key]
        self.processsingleDropJumpfile(self.current_file_left)

    # Dropdown (Right) changed method
    def on_file_combobox_right_changed(self):
        file_key = self.fileComboBoxRight.currentText()
        self.current_file_right = self.file_path_dict[file_key]
        self.processsingleDropJumpfile(self.current_file_right)

    # For dragging in new files        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
                
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]  # Remove .csv extension
                self.file_path_dict[file_name] = file_path
                
                if 'LEFT' in file_name.upper():
                    if self.fileComboBoxLeft.findText(file_name) == -1:
                        self.fileComboBoxLeft.addItem(file_name)
                    self.fileComboBoxLeft.setCurrentText(file_name)
                    self.current_file_left = file_path
                    self.on_file_combobox_left_changed()
                    self.left_drop_count = self.left_drop_count + 1
                    self.processsingleDropJumpfile(file_path)
                    self.average_data(self.outcome_dat)

                if 'RIGHT' in file_name.upper():
                    if self.fileComboBoxRight.findText(file_name) == -1:
                        self.fileComboBoxRight.addItem(file_name)
                    self.right_drop_count = self.right_drop_count + 1
                    self.fileComboBoxRight.setCurrentText(file_name)
                    self.current_file_right = file_path
                    self.on_file_combobox_right_changed()
                    self.processsingleDropJumpfile(file_path)
                    self.average_data(self.outcome_dat)
                    
    # now the processing script
    def processsingleDropJumpfile(self, file_path):
        # constants
        sf = 1000
        pt_mass = self.pt_mass
        pt_weight = pt_mass * 9.81
        bodymass = pt_mass
        drop_height = self.drop_height
        box_height = drop_height
        impact_velo = np.sqrt(2 * 9.81 * drop_height) * -1
        outcome_dat = self.outcome_dat
        
        # pull file name and time of creation
        file_name = os.path.basename(file_path)[:-4]
        
        if 'LEFT' in file_name.upper():
            self.jump_leg_name = 'LEFT'
        if 'RIGHT' in file_name.upper():
            self.jump_leg_name = 'RIGHT'
        
        # read in data
        dat = pd.read_csv(file_path)
        
        fz_jump_leg = dat.iloc[:, self.fz_col]
        fz_total = fz_jump_leg
        
        # calculate time
        trial_len = len(fz_total)
        trial_time = trial_len/sf
        time_s = np.linspace(start = 0, stop = trial_time, num = trial_len)
        
        # find ground contact
        ground_contact = 500
        while fz_total[ground_contact] < 30:
            ground_contact = ground_contact + 1
        time_ground_contact_s = time_s[ground_contact]
        
        # takeoff calculation
        takeoff = ground_contact + 1
        while fz_total[takeoff] > 30:
            takeoff = takeoff + 1
        time_takeoff_s = time_s[takeoff]
        
        # land calculation
        land = takeoff + 250
        while fz_total[land] < 30:
            land = land + 1
        time_land_s = time_s[land]
        
        
        # end land calculation
        end_land = land+200
        while fz_total[end_land] > pt_weight:
            end_land = end_land + 1
        while fz_total[end_land] < pt_weight:
            end_land = end_land -1
        # sanity check
        if end_land > land:
            end_land = end_land
        else:
            end_land = land+500
        time_end_land_s = time_s[end_land]
        
        # initial crop of arays from ground contact to end landing
        fz_total_cropped = fz_total[ground_contact:end_land]
        fz_net_cropped = fz_total_cropped - pt_weight # net (vGRF - pt weight)
        time_cropped_s = time_s[ground_contact:end_land]
        
        # calculate acceleration
        accel = np.array(fz_net_cropped / bodymass)
        
        # calculate velocity with a custom function, this is because
        # int_cumptraz no longer takes an initial argument (e.g., impact velo)
        # and we are not really interested in the drop phase velocity
        velo = [0] * len(accel) # empty array of 0s length of accel array
        velo[0] = impact_velo # set first value to impact velocity
        # loop that performs cumulative integration on the cropped arays
        for i in range(1, len(accel)):
            velo[i] = accel[i] * (time_cropped_s[i] - time_cropped_s[i-1]) + velo[i-1]
        # make sure velocity is an array and not a list
       # print(velo)
        velo = np.array(velo)
        #print(len(velo))
        
        # now we can calculate phases
        # concnetric based on when velocity crosses 0
        start_concentric = 1
        while velo[start_concentric] < 0:
            start_concentric = start_concentric + 1
        time_cropped_at_start_concentric_s = time_cropped_s[start_concentric]
        
        # get indices for time in the cropped array
        time_cropped_takeoff_index = np.where(time_cropped_s == time_takeoff_s)[0][0]
        time_cropped_land_index = np.where(time_cropped_s == time_land_s)[0][0]
        time_cropped_end_land_index = len(velo) # for now, end of landing phase is the lenght of velo
        
        # lastly, full time array at start concentric
        full_index_at_start_concentric = np.where(time_s == time_cropped_at_start_concentric_s)[0][0]
        time_s_at_start_concentric = time_s[full_index_at_start_concentric]
        
        ##### Phase Calculations
        # total force arrays
        ecc_fz_total = fz_total[ground_contact:full_index_at_start_concentric]
        con_fz_total = fz_total[full_index_at_start_concentric:takeoff]
        land_fz_total = fz_total[land:end_land]
        positive_fz_total = fz_total[ground_contact:takeoff]
        
        # velocity arrays
        ecc_velo = velo[0:start_concentric]
        con_velo = velo[start_concentric:time_cropped_takeoff_index]
        land_velo = velo[time_cropped_land_index:time_cropped_end_land_index]
        
        # power arrays
        ecc_power = ecc_velo * ecc_fz_total
        con_power = con_velo * con_fz_total
        land_power = land_velo * land_fz_total
        
        ##### Outcomes start here
        # power outcomes
        ecc_peak_power = ecc_power.min()
        ecc_mean_power = ecc_power.mean()
        con_peak_power = con_power.max()
        con_mean_power = con_power.mean()
        land_peak_power = land_power.min()
        land_mean_power = land_power.mean()    
        
        # kinetic phase specific outcomes
        # eccentric
        ecc_peak_force_n = ecc_fz_total.max()
        ecc_peak_force_nkg = ecc_peak_force_n/bodymass    
        ecc_mean_force_n = ecc_fz_total.mean()
        ecc_mean_force_nkg = ecc_mean_force_n/bodymass
        ecc_impulse = int_trapz(ecc_fz_total)/sf
        # concentric
        con_peak_force_n = con_fz_total.max()
        con_peak_force_nkg = con_peak_force_n/bodymass    
        con_mean_force_n = con_fz_total.mean()
        con_mean_force_nkg = con_mean_force_n/bodymass
        con_impulse = int_trapz(con_fz_total)/sf
        positive_impulse = int_trapz(positive_fz_total)/sf
        # land
        land_peak_force_n = land_fz_total.max()
        land_peak_force_nkg = land_peak_force_n/bodymass    
        land_mean_force_n = land_fz_total.mean()
        land_mean_force_nkg = land_mean_force_n/bodymass
        land_impulse = int_trapz(land_fz_total)/sf
        
        # velocity outcomes
        con_peak_velocity = con_velo.max()
        con_mean_velocity = con_velo.mean()
        ecc_mean_velocity = ecc_velo.mean()
        land_peak_velocity = land_velo.min()
        land_mean_velocity = land_velo.mean()
        
        # time constrained outcomes
        groundcontact_time_s = time_s[takeoff] - time_s[ground_contact]
        ecc_time_s = time_s_at_start_concentric - time_ground_contact_s
        con_time_s = time_takeoff_s - time_s_at_start_concentric
        flight_time_s = time_land_s - time_takeoff_s
        land_time_s = time_end_land_s - time_land_s
        
        # performance outcomes
        vto = velo[time_cropped_takeoff_index]
        jh_m = ((vto ** 2))/(9.81 * 2)
        jh_cm = jh_m * 100
        rsi = flight_time_s/time_ground_contact_s
        
        # aggregate into a list
        values_dat = [bodymass, box_height, jh_cm, rsi,
                    con_peak_power, ecc_peak_power, land_peak_power,
                    con_mean_power, ecc_mean_power, land_mean_power,
                    con_peak_force_n, con_peak_force_nkg, ecc_peak_force_n,
                    ecc_peak_force_nkg, con_mean_force_n, con_mean_force_nkg,
                    ecc_mean_force_n, ecc_mean_force_nkg, land_peak_force_n,
                    land_peak_force_nkg, land_mean_force_n, land_mean_force_nkg,
                    con_impulse, ecc_impulse, positive_impulse,
                    land_impulse, groundcontact_time_s, ecc_time_s,
                    con_time_s, flight_time_s, land_time_s,
                    con_peak_velocity, land_peak_velocity, land_mean_velocity,
                    con_mean_velocity, ecc_mean_velocity, vto]
        
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n), 3) for n in values_dat]
        
        full_table_vars = list(singleplate_dropjump_vars_dict.values())
        self.display_table(self.outcome_dat)
        outcome_dat[file_name] = values_dat_clean
        
        ##### Plotting
        time_at_ground_contact_s = time_s[ground_contact]
        time_at_start_concentric_s = time_s_at_start_concentric
        time_at_takeoff_s = time_s[takeoff]
        time_at_land_s = time_s[land]
        
        # for adding annotations
        annotations = {'Ground Contact': time_at_ground_contact_s,
                       'Concentric': time_at_start_concentric_s,
                       'Flight': time_at_takeoff_s,
                       'Landing': time_at_land_s+0.1}
        
        if 'LEFT' in file_name.upper():
            col_jump = 'blue'
            self.figure1.clear()
            ax = self.figure1.add_subplot(111)
            #figure itself
            ax.axvline(x = time_at_ground_contact_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_start_concentric_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_takeoff_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_land_s, ls = ":", color = 'grey', lw = 0.4)
            sns.lineplot(x = time_s[ground_contact-500:], y = fz_total[ground_contact-500:], color = col_jump, ax = ax)
            ax.xaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
            ax.set_ylabel('Force (N)')
            ax.set_xlabel('Time (seconds)')
            y_pos = ax.get_ylim()[1]*0.95 # annotations code below
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                            textcoords = 'offset points', ha = 'left', va = 'top',
                            fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure1.tight_layout();
            self.canvas1.draw()
        if 'RIGHT' in file_name.upper():
            col_jump = 'red'
            self.figure2.clear()
            ax = self.figure2.add_subplot(111)
            #figure itself
            ax.axvline(x = time_at_ground_contact_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_start_concentric_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_takeoff_s, ls = ":", color = 'grey', lw = 0.4)
            ax.axvline(x = time_at_land_s, ls = ":", color = 'grey', lw = 0.4)
            sns.lineplot(x = time_s[ground_contact-500:], y = fz_total[ground_contact-500:], color = col_jump, ax = ax)
            ax.xaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
            ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
            ax.set_ylabel('Force (N)')
            ax.set_xlabel('Time (seconds)')
            y_pos = ax.get_ylim()[1]*0.95 # annotations code below
            for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                            textcoords = 'offset points', ha = 'left', va = 'top',
                            fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
            self.figure2.tight_layout();
            self.canvas2.draw()
        self.outcome_dat = outcome_dat # again for emphasis?
        
    # custom function for average data
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:,0]
        var_names = var_names[1:]
        left_columns = dataframe.loc[:, dataframe.columns.str.contains("LEFT")]
        right_columns = dataframe.loc[:, dataframe.columns.str.contains("RIGHT")]
        left_columns_mean = left_columns.mean(axis = 1)
        left_columns_mean = left_columns_mean[1:]
        left_columns_mean = left_columns_mean.round(3)
        right_columns_mean = right_columns.mean(axis = 1)
        right_columns_mean = right_columns_mean[1:]
        right_columns_mean = right_columns_mean.round(3)
        left_right_lsi = left_columns_mean/right_columns_mean
        left_right_lsi = left_right_lsi.round(3)
        right_left_lsi = right_columns_mean/left_columns_mean
        right_left_lsi = right_left_lsi.round(3)
        average_dat = pd.DataFrame({"Variable": var_names,
                                    "Left": left_columns_mean,
                                    "Right": right_columns_mean,
                                    "L/R LSI": left_right_lsi,
                                    "R/L LSI": right_left_lsi})        
        self.average_dat = average_dat
    
    # other custom functions    
    # defining export data function
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        average_df = self.average_dat
        outcome_df = self.outcome_dat        
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += '.xlsx'
            with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = "Individual Data", index = False)
                 
    def returntoHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()
    
    def closeApp(self):
        self.close()       
        
        
##### Now for the CMJ analysis        
class SinglePlateCMJAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        # File dictionary to enable handling of multiple files
        self.file_path_dict = {}
        self.current_file = None
        self.table_dat = pd.DataFrame()
        
        # Initialize dataframes 
        self.outcome_dat =  pd.DataFrame({'Variable': singleplate_cmj_vars_dict.values()})
        
        # Display the default table (outcome_dat)
        self.display_table(self.table_dat)
        self.drop_count = 0
        
        # Initialize the VariableSelectionDialog with the data dictionary
        self.cmj_vars_dict = singleplate_cmj_vars_dict
       
    def initUI(self):
        self.setWindowTitle("CMJ Analysis- Single Plate")
        self.setGeometry(100, 100, 1600, 800)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout()  # for plots
        self.rightLayout = QVBoxLayout()  # for table
     
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2) 
        
        # Create a dropdown box for selecting files for the left plot
        self.fileComboBox = QComboBox()
        self.fileComboBox.currentIndexChanged.connect(self.on_file_combobox_changed)
        self.leftLayout.addWidget(self.fileComboBox)

        # Label for left plot file selection
        self.label = QLabel("Drag and Drop CMJ Trial(s) here:", self)
        self.label.setFont(QFont("Arial bold", 10))
        self.label.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label)

        # First plot (Left)
        self.figure = plt.Figure(figsize=(12, 16))
        self.canvas = FigureCanvas(self.figure)
        self.leftLayout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates = False)
        self.leftLayout.addWidget(self.toolbar)
        
        # defining the table for values
        # Create a QComboBox for selecting data displayed in table
        self.comboBox = QComboBox()
        self.comboBox.addItems(['Full Results', "Average Results"])
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.rightLayout.addWidget(self.comboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)   
            
        # Adding in buttons
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # Add export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
                     
        # Quit program button       
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton) 
        
        # home button
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returntoHome)
        self.buttonLayout.addWidget(self.homeButton)
        
        # odd spot
        self.setAcceptDrops(True)
                
        self.topLayout.addLayout(self.buttonLayout)
        
        # Column selection for safety of making sure
        self.columnSelectionPrompt()   

    # Define column selection prompt page
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_col, ok1 = QInputDialog.getItem(self, "Select Column", "Select 'Fz' Column from Excel file, double check this prior \nto any analyses or the program will not run:", columnOptions, 5, False)
        if ok1:
            self.fz_col = ord(self.fz_col) - 65
        else:
            self.close()
    
     # Method to update the table display       
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        variable_font = QFont()
        variable_font.setBold(True)
        variable_font.setFamily("Arial")
        variable_font.setPointSize(8)    
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(8)
     
        # Loop through the dataframe to populate the table
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i, j]
                if j == 0:  # First column (strings)
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:  # Second and subsequent columns (floats)
                    numeric_value = float(value)
                    item = QTableWidgetItem(f"{numeric_value:.2f}")
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
        
    # Update the on_combobox_changed method to handle three dataframes this needs to be modifed
    def on_combobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.average_data(self.outcome_dat)
            self.display_table(self.average_dat)  

    # Dropdown file changed method
    def on_file_combobox_changed(self):
        file_key = self.fileComboBox.currentText()
        self.current_file = self.file_path_dict[file_key]
        self.processCMJfile(self.current_file)

    # For dragging in new files        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
                
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]  # Remove .csv extension
                self.file_path_dict[file_name] = file_path
                self.processCMJfile(file_path)
                if self.fileComboBox.findText(file_name) == -1:
                    self.fileComboBox.addItem(file_name)
                self.fileComboBox.setCurrentText(file_name)
                self.current_file = file_path
                self.on_combobox_changed(0)
               
    # Process the SLJ file(s) 
    def processCMJfile(self, file_path):
        outcome_dat = self.outcome_dat
        file_name = os.path.basename(file_path)[:-4]

        dat = pd.read_csv(file_path)

        
        fz_total = dat.iloc[:, self.fz_col]
        
        # would prefer for this to be a whole 1-3 seconds. 
        bw_mean = fz_total[0:1500].mean()
        bw_sd = fz_total[0:1500].std()
        bodymass = bw_mean / 9.81
        
        # calculate time
        sf = 1000
        dat_len = len(fz_total)
        trial_time = dat_len / sf
        time_s = np.linspace(start = 0, stop = trial_time, num = dat_len)
        
        # calculate other arrays
        accel = (fz_total - bw_mean) / bodymass
        velo = int_cumtrapz(x = time_s, y = accel) 
        position = int_cumtrapz(x = time_s[1:], y = velo)
        power = fz_total[1:] * velo

        start_move = 20
        while fz_total[start_move] > (bw_mean - (bw_sd  * 5)):
            start_move = start_move + 1
        while fz_total[start_move] < bw_mean:
                start_move = start_move - 1
            
        takeoff = start_move 
        while fz_total[takeoff] > 30:
            takeoff = takeoff + 1
            
        start_ecc_velo = min(velo[start_move:takeoff])
        start_ecc = list(velo).index(start_ecc_velo)
        
        start_con = start_ecc
        while velo[start_con] < 0:
            start_con = start_con + 1    
            
        land = takeoff + 150
        while fz_total[land] < 30:
            land = land + 1
            
        end_land = land + 100
        while fz_total[end_land] > bw_mean:
            end_land = end_land + 1
        while fz_total[end_land] < bw_mean:
            end_land = end_land - 1        
            
        ### Make arrays for each phase - force
        unweigh_fz = fz_total[start_move:start_ecc]
        ecc_fz = fz_total[start_ecc:start_con]
        con_fz = fz_total[start_con:takeoff]
        land_fz = fz_total[land:end_land]
        positive_fz = fz_total[start_ecc:takeoff]
        
        ### - velo
        unweigh_velo = velo[start_move:start_ecc]
        ecc_velo = velo[start_ecc:start_con]
        con_velo = velo[start_con:takeoff]
        land_velo = velo[land:end_land]
                
        ### - power 
        ecc_power = power[start_ecc:start_con]
        con_power = power[start_con:takeoff]
        land_power = power[land:end_land]
                
        ##### Power outcomes 
        ecc_peak_power = ecc_power.min()
        ecc_mean_power = ecc_power.mean()
        con_peak_power = con_power.max()
        con_mean_power = con_power.mean()
        land_peak_power = land_power.max()
        land_mean_power = land_power.mean()
        
        ##### Kinetic phase-specific outcome variables
        ### TOTAL kinetic phase outcome variables
        # eccentric
        ecc_peak_force_n = ecc_fz.max()
        ecc_peak_force_nkg = ecc_peak_force_n/bodymass
        ecc_mean_force_n = ecc_fz.mean()
        ecc_mean_force_nkg = ecc_mean_force_n/bodymass
        ecc_impulse = int_trapz(ecc_fz)/sf
                
        # concentric
        con_peak_force_n = con_fz.max()
        con_peak_force_nkg = con_peak_force_n/bodymass
        con_mean_force_n = con_fz.mean()
        con_mean_force_nkg = con_mean_force_n/bodymass
        con_impulse = int_trapz(con_fz)/sf
                
        # positve impulse
        positive_impulse = int_trapz(positive_fz)/sf
            
        # landing
        land_peak_force_n = land_fz.max()
        land_peak_force_nkg = land_peak_force_n/bodymass
        land_mean_force_n = land_fz.mean()
        land_mean_force_nkg = land_mean_force_n/bodymass
        land_impulse = int_trapz(land_fz)/sf   
                
        ##### Time specific outcomes
        unweigh_dur = time_s[start_ecc] - time_s[start_move]
        contraction_time_s = time_s[takeoff] - time_s[start_move]
        ecc_time_s = time_s[start_con] - time_s[start_ecc]
        con_time_s = time_s[takeoff] - time_s[start_con]
        flight_time_s = time_s[land] - time_s[takeoff]
        land_time_s = time_s[end_land] - time_s[land]        
                
        ##### RFD outcomes
        ecc_rfd = (fz_total[start_con] - fz_total[start_ecc]) / ecc_time_s
        con_rfd = (fz_total[start_con] - fz_total[takeoff]) / con_time_s
        land_rfd = (fz_total[end_land] - fz_total[land]) / land_time_s
            
        ##### Velocity outcomes
        ecc_peak_velocity = ecc_velo.min()
        con_peak_velocity = con_velo.max()
        ecc_mean_velocity = ecc_velo.mean()
        con_mean_velocity = con_velo.mean()
        land_peak_velocity = land_velo.min()
                                
        ##### Outcome variables
        vto = velo[takeoff]
        jh = ((vto ** 2)/(9.81 * 2))
        jh_cm = jh * 100
        mrsi = jh/contraction_time_s
        depth = position[start_move:takeoff].min()
        cm_depth = depth * 100
            
        # combine into a list
        values_dat = [bodymass,
                        jh_cm,
                        mrsi,
                        con_peak_power,
                        ecc_peak_power,
                        land_peak_power,
                        con_mean_power,
                        ecc_mean_power,
                        land_mean_power,
                        con_peak_force_n,
                        con_peak_force_nkg,
                        ecc_peak_force_n,
                        ecc_peak_force_nkg,
                        con_mean_force_n,
                        con_mean_force_nkg,
                        ecc_mean_force_n,
                        ecc_mean_force_nkg,
                        land_peak_force_n,
                        land_peak_force_nkg,
                        land_mean_force_n,
                        land_mean_force_nkg,
                        con_impulse,
                        ecc_impulse,
                        positive_impulse,
                        land_impulse,
                        con_rfd,
                        ecc_rfd,
                        land_rfd,
                        unweigh_dur,
                        ecc_time_s,
                        con_time_s,
                        contraction_time_s,
                        flight_time_s,
                        land_time_s,
                        con_peak_velocity,
                        ecc_peak_velocity,
                        land_peak_velocity,
                        con_mean_velocity,
                        ecc_mean_velocity,
                        vto,
                        cm_depth]

        
        # round with list comprehension
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n),3) for n in values_dat]
                        

        self.display_table(self.outcome_dat) # display data in table
        
        outcome_dat[file_name] = values_dat_clean 
        
        # Define time outcomes for plotting  
        start_move_s = time_s[start_move]
        start_ecc_s = time_s[start_ecc]
        start_con_s = time_s[start_con]
        takeoff_s = time_s[takeoff]
        land_s = time_s[land]
        end_land_s = time_s[end_land]
        
        # For adding annotations             
        annotations = {"Unweigh": start_move_s, 
                       "Ecentric": start_ecc_s, 
                       "Concentric": start_con_s, 
                       "Flight": takeoff_s, 
                       "Landing": land_s+0.1}
        
        # figure
        self.figure.clear()   
        ax = self.figure.add_subplot(111)    
        ax.axhline(y = bw_mean, color = 'black', ls = "--", lw = 0.4)
        ax.axvline(x = start_move_s, ls = ":", color = 'black', lw = 0.4)
        ax.axvline(x = start_ecc_s, ls = ':', color = 'black', lw = 0.4)
        ax.axvline(x = start_con_s, ls = ":", color = 'black', lw = 0.4)
        ax.axvline(x = takeoff_s, ls = ":", color = 'black', lw = 0.4)
        ax.axvline(x = land_s, ls = ":", color = 'black', lw = 0.4)
        ax.axvline(x = end_land_s, ls = ":", color = 'black', lw = 0.4)
        sns.lineplot(x=time_s[0:end_land+500], y=fz_total[0:end_land+500], color= 'black', ax=ax)
        ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both'))
        ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
        ax.set_ylabel("Force (N)")
            
        y_pos = ax.get_ylim()[1]*0.95
        # add annotations to force plt
        for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
        self.figure.tight_layout();    
        self.canvas.draw()
        self.outcome_dat = outcome_dat  
    
    # average data
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        values_dat = dataframe.iloc[:,1:]
        values_dat_mean = values_dat.mean(axis = 1)       
        average_dat = pd.DataFrame({"Variable": var_names,
                                    "Value": values_dat_mean})
        self.average_dat = average_dat     
    
    # defining export data function
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "XLSX Files (*.xlsx);;All Files (*)", options=options)
        average_df = self.average_dat
        outcome_df = self.outcome_dat    
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += '.xlsx'
            with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
                average_df.to_excel(writer, sheet_name = 'Average Data', index = False)
                outcome_df.to_excel(writer, sheet_name = "Individual Data", index = False)
    def returntoHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()           
    def closeApp(self):
        self.close()
        
class DualPlateCMJAnalysisWindow(QMainWindow):       
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        # File dictionary to enable handling of multiple files
        self.file_path_dict = {}
        self.current_file = None
        self.table_dat = pd.DataFrame()
        
        # Initialize dataframes 
        self.outcome_dat =  pd.DataFrame({'Variable': dualplate_cmj_vars_dict.values()})
        self.selected_vars = []
        
        # Display the default table (outcome_dat)
        self.display_table(self.table_dat)
        self.drop_count = 0
        
    def initUI(self):
        self.setWindowTitle("Dual Plate CMJ Analysis")
        self.setGeometry(100, 100, 1600, 800)
                
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout() # plots
        self.rightLayout = QVBoxLayout() # table
        
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2)
        
        # dropdown box for file plot selection
        self.fileComboBox = QComboBox()
        self.fileComboBox.currentIndexChanged.connect(self.on_file_combobox_changed)
        self.leftLayout.addWidget(self.fileComboBox)
        
        # label for left plot file selection
        self.label = QLabel("Drag and Drop CMJ Trial(s) here:", self)
        self.label.setFont(QFont("Arial bold", 10))
        self.label.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label)
        
        # cmj plot
        self.figure = plt.Figure(figsize = (12,16))
        self.canvas = FigureCanvas(self.figure)
        self.leftLayout.addWidget(self.canvas)
        
        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates = False)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        
        # define table for values
        self.tableComboBox = QComboBox()
        self.tableComboBox.addItems(["Full Results", "Average Results", "LSI Results"])
        self.tableComboBox.currentIndexChanged.connect(self.on_tablecombobox_changed)
        self.rightLayout.addWidget(self.tableComboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # buttons for things, save data, quit program, eventually add back in go to home screen button
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
        
        # close program button
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton)
        
        # return to home screen button
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returntoHome)
        self.buttonLayout.addWidget(self.homeButton)
                
        self.topLayout.addLayout(self.buttonLayout)
        
        # column selection
        self.columnSelectionPrompt()
        
        # for dropping
        self.setAcceptDrops(True)
        
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_left_col, ok1 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Left Column from Excel file', columnOptions, 5, False)
        self.fz_right_col, ok2 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Right Column from Excel file', columnOptions, 16, False)
        
        if ok1 and ok2:
            self.fz_left_col = ord(self.fz_left_col) - 65
            self.fz_right_col = ord(self.fz_right_col) - 65
        else:
            self.close()
            
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        
        variable_font = QFont()
        variable_font.setBold(True)
        variable_font.setFamily('Arial')
        variable_font.setPointSize(8)
        value_font = QFont()
        value_font.setFamily('Arial')
        value_font.setPointSize(8)
        
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i,j]
                if j == 0:
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:
                    numeric_value = float(value)
                    item = QTableWidgetItem(f'{numeric_value:.2f}')
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i , j, item)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
    
    # actions for changing what values are displayed in the table     
    def on_tablecombobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.display_table(self.average_dat)
        if index == 2:
            self.display_table(self.lsi_data)
    
    # actions for changing what plot is displayed
    def on_file_combobox_changed(self):
        file_key = self.fileComboBox.currentText()
        self.current_file = self.file_path_dict[file_key]
        self.processdualCMJfile(self.current_file)
    
    # functions for dropping new files    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]
                self.file_path_dict[file_name] = file_path
                self.processdualCMJfile(file_path) # process the file
                self.average_data(self.outcome_dat) # calculate averages
                self.get_lsi(self.average_dat)  # calculate LSIs
                if self.fileComboBox.findText(file_name) == -1:
                    self.fileComboBox.addItem(file_name)
                self.fileComboBox.setCurrentText(file_name)
                self.current_file = file_path
                self.on_tablecombobox_changed(0)
    
    # now, the processing a dual plate CMJ                
    def processdualCMJfile(self, file_path):
        outcome_dat = self.outcome_dat
        file_name = os.path.basename(file_path)[:-4]
        # pull test date from file
        
        dat = pd.read_csv(file_path)
        #dat = dat.iloc[1000:]
        #dat.reset_index(inplace = True, drop = True)
        
        # read force columns
        fz_left = dat.iloc[:, self.fz_left_col]
        fz_right = dat.iloc[:, self.fz_right_col]
        fz_total = fz_left + fz_right
        
        bw_mean = fz_total[0:1500].mean()
        bw_sd = fz_total[0:1500].std()
        
        bodymass = bw_mean / 9.81
        
        # calculate time
        sf = 1000
        trial_len = len(fz_total)
        trial_time = trial_len/sf
        time_s = np.linspace(start = 0, stop = trial_time, num = trial_len)
        
        # calcualte accel, velo, position, and power
        accel = (fz_total - bw_mean) / bodymass
        velo = int_cumtrapz(x = time_s, y = accel)
        position = int_cumtrapz(y = velo, x = time_s[1:len(dat)])
        power = fz_total[1:len(fz_total)] * velo
        
        # identify indices
        start_move = 20
        while fz_total[start_move] > (bw_mean - (bw_sd * 5)):
            start_move = start_move + 1
        while fz_total[start_move] < bw_mean:
            start_move = start_move - 1
            
        # takeoff indices
        takeoff = start_move
        while fz_total[takeoff] > 30:
            takeoff = takeoff + 1
        
        # Eccentric phase index
        start_ecc_velo = min(velo[start_move:takeoff])
        start_ecc = list(velo).index(start_ecc_velo)
        
        # Concentric phase index
        start_con = start_ecc
        while velo[start_con] < 0:
            start_con = start_con  + 1 
            
        # landing phase indices
        land = takeoff + 150
        while fz_total[land] < 30:
            land = land + 1
            
        end_land = land + 500
        while fz_total[end_land] < bw_mean:
            end_land = end_land + 1
        while fz_total[end_land] < bw_mean:
            end_land = end_land - 1
        
        # make total arrays for each phase - force first
        unweigh_fz_total = fz_total[start_move:start_ecc]
        ecc_fz_total = fz_total[start_ecc:start_con]
        con_fz_total = fz_total[start_con:takeoff]
        land_fz_total = fz_total[land:end_land]
        positive_fz_total = fz_total[start_ecc:takeoff]
        
        # left force arrays
        unweigh_fz_left = fz_left[start_move:start_ecc]
        ecc_fz_left = fz_left[start_ecc:start_con]
        con_fz_left = fz_left[start_con:takeoff]
        land_fz_left = fz_left[land:end_land]
        positive_fz_left = fz_left[start_ecc:takeoff]
        
        # right force arrays
        unweigh_fz_right = fz_right[start_move:start_ecc]
        ecc_fz_right = fz_right[start_ecc:start_con]
        con_fz_right = fz_right[start_con:takeoff]
        land_fz_right = fz_right[land:end_land]
        positive_fz_right = fz_right[start_ecc:takeoff]
        
        # velocity arrays
        unweigh_velo = velo[start_move:start_ecc]
        ecc_velo = velo[start_ecc:start_con]
        con_velo = velo[start_con:takeoff]
        land_velo = velo[land:end_land]
        
        # power arrays
        ecc_power = power[start_ecc:start_con]
        con_power = power[start_con:takeoff]
        land_power = power[land:end_land]
        
        ##### Outcomes Start Here
        # power outcomes
        ecc_peak_power = ecc_power.min()
        ecc_mean_power = ecc_power.mean()
        con_peak_power = con_power.max()
        con_mean_power = con_power.mean()
        land_peak_power = land_power.max()
        land_mean_power = land_power.mean()
        
        # Total Kinetic Phase Specific Outcomes
        # eccentric 
        total_ecc_peak_force_n = ecc_fz_total.max()
        total_ecc_peak_force_nkg = total_ecc_peak_force_n/bodymass
        total_ecc_mean_force_n = ecc_fz_total.mean()
        total_ecc_mean_force_nkg = total_ecc_mean_force_n/bodymass
        total_ecc_impulse = int_trapz(ecc_fz_total)/sf
        
        # concentric
        total_con_peak_force_n = con_fz_total.max()
        total_con_peak_force_nkg = total_con_peak_force_n/bodymass
        total_con_mean_force_n = con_fz_total.mean()
        total_con_mean_force_nkg = total_con_mean_force_n/bodymass
        total_con_impulse = int_trapz(con_fz_total)/sf
        
        # positive impulses
        total_positive_impulse = int_trapz(positive_fz_total)/sf
        left_positive_impulse = int_trapz(positive_fz_left)/sf
        right_positive_impulse = int_trapz(positive_fz_right)/sf
        
        # landing
        total_land_peak_force_n = land_fz_total.max()
        total_land_peak_force_nkg = total_land_peak_force_n/bodymass
        total_land_mean_force_n = land_fz_total.mean()
        total_land_mean_force_nkg = total_land_mean_force_n/bodymass
        total_land_impulse = int_trapz(land_fz_total)/sf
        
        # Left Leg Phase Specific Outcomes
        # eccentric 
        left_ecc_peak_force_n = ecc_fz_left.max()
        left_ecc_peak_force_nkg = left_ecc_peak_force_n/bodymass
        left_ecc_mean_force_n = ecc_fz_left.mean()
        left_ecc_mean_force_nkg = left_ecc_mean_force_n/bodymass
        left_ecc_impulse = int_trapz(ecc_fz_left)/sf
        
        # concentric
        left_con_peak_force_n = con_fz_left.max()
        left_con_peak_force_nkg = left_con_peak_force_n/bodymass
        left_con_mean_force_n = con_fz_left.mean()
        left_con_mean_force_nkg = left_con_mean_force_n/bodymass
        left_con_impulse = int_trapz(con_fz_left)/sf
        
        # landing
        left_land_peak_force_n = land_fz_left.max()
        left_land_peak_force_nkg = left_land_peak_force_n/bodymass
        left_land_mean_force_n = land_fz_left.mean()
        left_land_mean_force_nkg = left_land_mean_force_n/bodymass
        left_land_impulse = int_trapz(land_fz_left)/sf
        
        # Right Leg Phase Specific Outcomes
        # eccentric 
        right_ecc_peak_force_n = ecc_fz_right.max()
        right_ecc_peak_force_nkg = right_ecc_peak_force_n/bodymass
        right_ecc_mean_force_n = ecc_fz_right.mean()
        right_ecc_mean_force_nkg = right_ecc_mean_force_n/bodymass
        right_ecc_impulse = int_trapz(ecc_fz_right)/sf
        
        # concentric
        right_con_peak_force_n = con_fz_right.max()
        right_con_peak_force_nkg = right_con_peak_force_n/bodymass
        right_con_mean_force_n = con_fz_right.mean()
        right_con_mean_force_nkg = right_con_mean_force_n/bodymass
        right_con_impulse = int_trapz(con_fz_right)/sf
        
        # landing
        right_land_peak_force_n = land_fz_right.max()
        right_land_peak_force_nkg = right_land_peak_force_n/bodymass
        right_land_mean_force_n = land_fz_right.mean()
        right_land_mean_force_nkg = right_land_mean_force_n/bodymass
        right_land_impulse = int_trapz(land_fz_right)/sf
        
        # time-constrained outcomes
        unweigh_dur = time_s[start_ecc] - time_s[start_move]
        ecc_time_s = time_s[start_con] - time_s[start_ecc]
        con_time_s = time_s[takeoff] - time_s[start_con]
        contraction_time_s = time_s[takeoff] - time_s[start_move]
        flight_time_s = time_s[land] - time_s[takeoff]
        land_time_s = time_s[end_land] - time_s[land]
        
        # RFD outcomes
        total_ecc_rfd = (fz_total[start_con] - fz_total[start_ecc]) / ecc_time_s
        total_con_rfd = (fz_total[start_con] - fz_total[takeoff]) / con_time_s
        total_land_rfd = (fz_total[end_land] - fz_total[land]) / land_time_s
        left_ecc_rfd = (fz_left[start_con] - fz_left[start_ecc]) / ecc_time_s
        left_con_rfd = (fz_left[start_con] - fz_left[takeoff]) / con_time_s
        left_land_rfd = (fz_left[end_land] - fz_left[land]) / land_time_s
        right_ecc_rfd = (fz_right[start_con] - fz_right[start_ecc]) / ecc_time_s
        right_con_rfd = (fz_right[start_con] - fz_right[takeoff]) / con_time_s
        right_land_rfd = (fz_right[end_land] - fz_right[land]) / land_time_s
        
        # Velocity outcomes
        ecc_peak_velocity = ecc_velo.min()
        ecc_mean_velocity = ecc_velo.mean()
        con_peak_velocity = con_velo.max()
        con_mean_velocity = con_velo.mean()
        land_peak_velocity = land_velo.min()
        
        # Performance outcomes
        vto = velo[takeoff]
        jh = ((vto ** 2)/(9.81 * 2))
        jh_cm = jh * 100
        mrsi = jh/contraction_time_s
        depth = position[start_move:takeoff].min()
        cm_depth = depth * 100
                
        # arrange values in a list
        values_dat = [bodymass, jh_cm, mrsi, 
                      con_peak_power, ecc_peak_power, land_peak_power, 
                      con_mean_power, ecc_mean_power, land_mean_power, 
                      total_con_peak_force_n, total_con_peak_force_nkg, total_ecc_peak_force_n, 
                      total_ecc_peak_force_nkg, total_con_mean_force_n, total_con_mean_force_nkg, 
                      total_ecc_mean_force_n, total_ecc_mean_force_nkg, total_land_peak_force_n, 
                      total_land_peak_force_nkg, total_land_mean_force_n, total_land_mean_force_nkg, 
                      total_con_impulse, total_ecc_impulse, total_positive_impulse, 
                      total_land_impulse, total_con_rfd, total_ecc_rfd, 
                      total_land_rfd, left_con_peak_force_n, left_con_peak_force_nkg, 
                      left_ecc_peak_force_n, left_ecc_peak_force_nkg, left_con_mean_force_n, 
                      left_con_mean_force_nkg, left_ecc_mean_force_n, left_ecc_mean_force_nkg, 
                      left_land_peak_force_n, left_land_peak_force_nkg, left_land_mean_force_n, 
                      left_land_mean_force_nkg, left_con_impulse, left_ecc_impulse, 
                      left_positive_impulse, left_land_impulse, left_con_rfd, 
                      left_ecc_rfd, left_land_rfd, right_con_peak_force_n, 
                      right_con_peak_force_nkg, right_ecc_peak_force_n, right_ecc_peak_force_nkg, 
                      right_con_mean_force_n, right_con_mean_force_nkg, right_ecc_mean_force_n, 
                      right_ecc_mean_force_nkg, right_land_peak_force_n, right_land_peak_force_nkg, 
                      right_land_mean_force_n, right_land_mean_force_nkg, right_con_impulse, 
                      right_ecc_impulse, right_positive_impulse, right_land_impulse, 
                      right_con_rfd, right_ecc_rfd, right_land_rfd, 
                      unweigh_dur, ecc_time_s, con_time_s, 
                      contraction_time_s, flight_time_s, land_time_s, 
                      con_peak_velocity, ecc_peak_velocity, land_peak_velocity, 
                      con_mean_velocity, ecc_mean_velocity, vto, cm_depth]
        
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n), 3) for n in values_dat]
        
        full_table_vars = list(dualplate_cmj_vars_dict.values())
                
        self.display_table(self.outcome_dat)
        outcome_dat[file_name] = values_dat_clean
        
        ##### Plotting
        start_move_s = time_s[start_move]
        start_ecc_s = time_s[start_ecc]
        start_con_s = time_s[start_con]
        takeoff_s = time_s[takeoff]
        land_s = time_s[land]
        end_land_s = time_s[end_land]
        
        # for adding annotations
        annotations = {'Unweigh': start_move_s,
                       'Eccentric': start_ecc_s,
                       'Concentric': start_con_s,
                       'Fight': takeoff_s,
                       'Landing': land_s+0.1}
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axhline(y = bw_mean, color = 'grey', ls = "--", lw = 0.4)
        ax.axvline(x = start_move_s, ls = ":", color = 'grey', lw = 0.4)
        ax.axvline(x = start_ecc_s, ls = ':', color = 'grey', lw = 0.4)
        ax.axvline(x = start_con_s, ls = ":", color = 'grey', lw = 0.4)
        ax.axvline(x = takeoff_s, ls = ":", color = 'grey', lw = 0.4)
        ax.axvline(x = land_s, ls = ":", color = 'grey', lw = 0.4)
        ax.axvline(x = end_land_s, ls = ":", color = 'grey', lw = 0.4)
        sns.lineplot(x = time_s[0:end_land+500], y = fz_total[0:end_land+500], label = "Total", color = "#0072B2", lw = 2, ax = ax)
        sns.lineplot(x = time_s[0:end_land+500], y = fz_left[0:end_land+500], label = "Left", color = "#D55E00", lw = 1, ax = ax)
        sns.lineplot(x = time_s[0:end_land+500], y = fz_right[0:end_land+500], label = 'Right', color = "#56B4E9", lw = 1, ax = ax)
        ax.xaxis.set_major_locator(MaxNLocator(integer = True, prune = 'both', nbins = 'auto'))
        ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
        ax.set_ylabel("Force (N)")
        ax.set_xlabel("Time (seconds)")
        ax.legend(loc = 'upper right', frameon = False)
            
        # add annotations to plot
        y_pos = ax.get_ylim()[1]*0.95
        for label, x_coord in annotations.items():
                ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                             textcoords = 'offset points', ha = 'left', va = 'top',
                             fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
        self.figure.tight_layout()    
        self.canvas.draw()
        self.outcome_dat = outcome_dat  
    
    # function to calculate averages        
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        
        values_dat = dataframe.iloc[:,1:]
        values_dat_mean = values_dat.mean(axis = 1)
        
        average_dat = pd.DataFrame({"Variable": var_names,
                                    "Average": values_dat_mean})
        
        self.average_dat = average_dat
       
    # function to get Limb symmetry indices 
    def get_lsi(self, dataframe):
        leg_data = dataframe[dataframe['Variable'].str.contains("Left|Right")].copy()
        leg_data['leg'] = leg_data['Variable'].apply(lambda x: 'Left' if 'Left' in x else 'Right')
        leg_data['Metric'] = leg_data['Variable'].apply(lambda x: x.split(' ', 1)[1])
        leg_data_clean = leg_data[['Metric', 'leg', 'Average']]
        leg_data_wide = leg_data_clean.pivot(index = 'Metric', columns = 'leg', values = 'Average').reset_index()
        leg_data_wide["L/R LSI"]  = np.round(leg_data_wide['Left'] / leg_data_wide['Right'], 2)
        leg_data_wide['R/L LSI'] = np.round(leg_data_wide['Right'] / leg_data_wide['Left'], 2)
        
        self.lsi_data = leg_data_wide       
        
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "XLSX Files (.xlsx);;All Files (*)", options = options)
        
        lsi_data = self.lsi_data
        average_df = self.average_dat
        outcome_df = self.outcome_dat
        
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += ".xlsx"
            with pd.ExcelWriter(save_path, engine = 'xlsxwriter') as writer:
                lsi_data.to_excel(writer, sheet_name = "LSI Data", index = False)
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = 'Individual Data', index = False)
        
        # for later
        # rel_dualplate_cmj_vars_dict = {key: value for key, value in dualplate_cmj_vars_dict.items() if not value.endswith("Force (N)")}
    
    def returntoHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()
    
    def closeApp(self):
        self.close()

# dual plate drop ladning analysies        
class DualPlateDropLandingAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        self.file_path_dict = {}
        self.current_file = None
        self.table_dat = pd.DataFrame()
        
        # initialize dataframes
        self.outcome_dat = pd.DataFrame({'Variable': dualplate_droplanding_vars_dict.values()})
        full_export_vars = list(dualplate_droplanding_vars_dict.values())
        full_export_vars.insert(0, 'Test Date')
        self.full_export_vars = full_export_vars
        self.export_dat = pd.DataFrame({"Variable": full_export_vars}) 
        
        # get user inputs (body mass)
        self.pt_mass = ()
        self.get_user_inputs()
        
        # display default table
        self.display_table(self.table_dat)
        self.drop_count = 0
    
    def initUI(self):
        self.setWindowTitle("Dual Plate Drop Landing Analysis")
        self.setGeometry(100, 100, 1600, 800)
                
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout() # plots
        self.rightLayout = QVBoxLayout() # table
        
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2)
        
        # dropdown box for file plot selection
        self.fileComboBox = QComboBox()
        self.fileComboBox.currentIndexChanged.connect(self.on_file_combobox_changed)
        self.leftLayout.addWidget(self.fileComboBox)
        
        # label for left plot file selection
        self.label = QLabel("Drag and Drop Drop Landing Trial(s) here:", self)
        self.label.setFont(QFont("Arial bold", 10))
        self.label.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label)
        
        # cmj plot
        self.figure = plt.Figure(figsize = (12,16))
        self.canvas = FigureCanvas(self.figure)
        self.leftLayout.addWidget(self.canvas)
        
        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates = False)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        
        # define table for values
        self.tableComboBox = QComboBox()
        self.tableComboBox.addItems(["Full Results", "Average Results", "LSI Results"])
        self.tableComboBox.currentIndexChanged.connect(self.on_tablecombobox_changed)
        self.rightLayout.addWidget(self.tableComboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # buttons for things, save data, quit program, eventually add back in go to home screen button
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
        
        # close program button
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton)
        
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returnToHome)
        self.buttonLayout.addWidget(self.homeButton)
        
        self.topLayout.addLayout(self.buttonLayout)
        
        # column selection
        self.columnSelectionPrompt()
        
        # for dropping
        self.setAcceptDrops(True)
    
    # custom function for user inputs
    def get_user_inputs(self):
        # input for participant's body mass
        pt_mass_lb, ok = QInputDialog.getDouble(self, "Input", "Enter Individual's Body Mass (pounds)- This must be accurate:", decimals = 2)
        if ok:
            pt_mass_kg = pt_mass_lb / 2.2046
            self.pt_mass = pt_mass_kg
        else:
            self.close()
        
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_left_col, ok1 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Left Column from Excel file', columnOptions, 5, False)
        self.fz_right_col, ok2 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Right Column from Excel file', columnOptions, 16, False)
        
        if ok1 and ok2:
            self.fz_left_col = ord(self.fz_left_col) - 65
            self.fz_right_col = ord(self.fz_right_col) - 65
        else:
            self.close()
            
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        
        variable_font = QFont("Arial bold", 8)
        value_font = QFont("Arial", 8)
        
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i,j]
                if j == 0:
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:
                    numeric_value = float(value)
                    item = QTableWidgetItem(f'{numeric_value:.2f}')
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i , j, item)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
    
    # actions for changing what values are displayed in the table     
    def on_tablecombobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.display_table(self.average_dat)
        if index == 2:
            self.display_table(self.lsi_data)
    
    # actions for changing what plot is displayed
    def on_file_combobox_changed(self):
        file_key = self.fileComboBox.currentText()
        self.current_file = self.file_path_dict[file_key]
        self.processdualDropfile(self.current_file)
    
    # functions for dropping new files    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]
                self.file_path_dict[file_name] = file_path
                self.processdualDropfile(file_path) # processs the file
                self.average_data(self.outcome_dat) # get averages
                self.get_lsi(self.average_dat) # get LSIs
                if self.fileComboBox.findText(file_name) == -1:
                    self.fileComboBox.addItem(file_name)
                self.fileComboBox.setCurrentText(file_name)
                self.current_file = file_path
                self.on_tablecombobox_changed(0)
                self.drop_count = self.drop_count + 1
                
    
    # processing a dual plate drop
    def processdualDropfile(self, file_path):
        sf = 1000
        pt_mass = self.pt_mass
        pt_weight = pt_mass * 9.81
        bodymass = pt_mass
        
        outcome_dat = self.outcome_dat
        export_dat = self.export_dat
        file_name = os.path.basename(file_path)[:-4]
        
        # read in data
        dat = pd.read_csv(file_path)
        
        # read force columns
        fz_left = dat.iloc[:, self.fz_left_col]
        fz_right = dat.iloc[:, self.fz_right_col]
        fz_total = fz_left + fz_right
        
        # time
        trial_len = len(fz_total)
        trial_time = trial_len/sf
        time_s = np.linspace(start = 0, stop = trial_time, num = trial_len)
        
        # determine indices
        impact = 500
        while fz_total[impact] < 30:
            impact = impact + 1
            
        impact_time_s = time_s[impact]
        
        # for later, transfer vGRF into units of BW
        fz_total_bwn = fz_total/pt_weight
        fz_left_bwn = fz_left/pt_weight
        fz_right_bwn = fz_right/pt_weight
        
        # identify peak values and their indices of time and index
        total_peak_force_n = fz_total.max()
        total_peak_force_nkg = total_peak_force_n/pt_mass
        total_peak_force_bwn = fz_total_bwn.max()
        total_peak_force_index = fz_total.argmax(axis = 0)
        total_peak_force_time_s = time_s[total_peak_force_index]
        
        left_peak_force_n = fz_left.max()
        left_peak_force_nkg = left_peak_force_n/pt_mass
        left_peak_force_bwn = fz_left_bwn.max()
        left_peak_force_index = fz_left.argmax(axis = 0)
        left_peak_force_time_s = time_s[left_peak_force_index]
        
        right_peak_force_n = fz_right.max()
        right_peak_force_nkg = right_peak_force_n/pt_mass
        right_peak_force_bwn = fz_right_bwn.max()
        right_peak_force_index = fz_right.argmax(axis = 0)
        right_peak_force_time_s = time_s[right_peak_force_index]
        
        # calculate times for loding rates
        time_to_total_peak_force_s = total_peak_force_time_s - impact_time_s
        time_to_left_peak_force_s = left_peak_force_time_s - impact_time_s
        time_to_right_peak_force_s = right_peak_force_time_s - impact_time_s
        
        # calculate loading rates
        total_loading_rate_bw_s = total_peak_force_bwn / time_to_total_peak_force_s
        left_loading_rate_bw_s = left_peak_force_bwn / time_to_left_peak_force_s
        right_loading_rate_bw_s = right_peak_force_bwn / time_to_right_peak_force_s

        
        # combine into a list
        values_dat = [bodymass, total_peak_force_n, total_peak_force_nkg,
                      left_peak_force_n, left_peak_force_nkg, right_peak_force_n,
                      right_peak_force_nkg, total_loading_rate_bw_s, left_loading_rate_bw_s,
                      right_loading_rate_bw_s]
        
        values_dat_clean = [round(float(n), 3) for n in values_dat]

        
        self.display_table(outcome_dat)
        outcome_dat[file_name] = values_dat_clean
        
        ##### Plotting
        annotations = {'Impact': impact_time_s,
                       'Peak Total Force': total_peak_force_time_s}
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axvline(x = impact_time_s, color = 'grey', ls = '--', lw = 0.4)
        ax.axvline(x = total_peak_force_time_s, color = 'grey', ls = '--', lw = 0.4)
        sns.lineplot(x = time_s[impact-500:], y = fz_total[impact-500:], label = 'Total', color = "#0072B2", lw = 2, ax = ax)
        sns.lineplot(x = time_s[impact-500:], y = fz_left[impact-500:], label = 'Left', color = "#D55E00", lw = 1, ax = ax)
        sns.lineplot(x = time_s[impact-500:], y = fz_right[impact-500:], label = 'Right', color = "#56B4E9", lw = 1, ax = ax)
        ax.xaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
        ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
        ax.set_ylabel('Force (N)')
        ax.set_xlabel('Time (seconds)')
        ax.legend(loc = 'upper right', frameon = False)
        
        # add annotations to plot
        y_pos = ax.get_ylim()[1]*0.95
        for label, x_coord in annotations.items():
            ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                        textcoords= 'offset points', ha = 'left', va = 'top',
                        fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
        self.figure.tight_layout()
        self.canvas.draw()
        self.outcome_dat = outcome_dat
        
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        values_dat = dataframe.iloc[:,1:]
        values_dat_mean = values_dat.mean(axis = 1)
        
        average_dat = pd.DataFrame({'Variable': var_names,
                                    'Average': values_dat_mean})
        
        self.average_dat = average_dat
   
    # function to get Limb symmetry indices 
    def get_lsi(self, dataframe):
        leg_data = dataframe[dataframe['Variable'].str.contains("Left|Right")].copy()
        leg_data['leg'] = leg_data['Variable'].apply(lambda x: 'Left' if 'Left' in x else 'Right')
        leg_data['Metric'] = leg_data['Variable'].apply(lambda x: x.split(' ', 1)[1])
        leg_data_clean = leg_data[['Metric', 'leg', 'Average']]
        leg_data_wide = leg_data_clean.pivot(index = 'Metric', columns = 'leg', values = 'Average').reset_index()
        leg_data_wide["L/R LSI"]  = np.round(leg_data_wide['Left'] / leg_data_wide['Right'], 2)
        leg_data_wide['R/L LSI'] = np.round(leg_data_wide['Right'] / leg_data_wide['Left'], 2)
        
        self.lsi_data = leg_data_wide  
                     
        
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "XLSX Files (.xlsx);;All Files (*)", options = options)
        
        lsi_df = self.lsi_data
        average_df = self.average_dat
        outcome_df = self.outcome_dat
        
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += ".xlsx"
            with pd.ExcelWriter(save_path, engine = 'xlsxwriter') as writer:
                lsi_df.to_excel(writer, sheet_name = "LSI Data", index = False)
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = 'Individual Data', index = False)
                
    def returnToHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()    
    
    def closeApp(self):
        self.close()
        
# Analysis of Dual Plate Drop Jumps
class DualPlateDropJumpAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()
        
        # file dictionary to enable handling of multiple files
        self.file_path_dict = {}
        self.current_file = None
        self.table_dat = pd.DataFrame()
        
        self.outcome_dat = pd.DataFrame({"Variable": dualplate_dropjump_vars_dict.values()})
        full_export_vars = list(dualplate_dropjump_vars_dict.values())
        full_export_vars.insert(0, 'Test Date')
        self.full_export_vars = full_export_vars
        self.export_dat = pd.DataFrame({'Variable': full_export_vars})
        
        # get user inputs (body mass and drop height)
        self.pt_mass = ()
        self.box_height = ()
        self.get_user_inputs()
        
        # display default table
        self.display_table(self.table_dat)
        self.drop_count = 0
    
    def initUI(self):
        self.setWindowTitle("Dual Plate Drop Jump Analysis")
        self.setGeometry(100, 100, 1600, 800)
                
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        self.layout = QVBoxLayout(self.centralWidget)
        self.topLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayout)
        self.leftLayout = QVBoxLayout() # plots
        self.rightLayout = QVBoxLayout() # table
        
        self.topLayout.addLayout(self.leftLayout, stretch = 3)
        self.topLayout.addLayout(self.rightLayout, stretch = 2)
        
        # dropdown box for file plot selection
        self.fileComboBox = QComboBox()
        self.fileComboBox.currentIndexChanged.connect(self.on_file_combobox_changed)
        self.leftLayout.addWidget(self.fileComboBox)
        
        # label for left plot file selection
        self.label = QLabel("Drag and Drop Drop Jump Trial(s) here:", self)
        self.label.setFont(QFont("Arial bold", 10))
        self.label.setAlignment(Qt.AlignLeft)
        self.leftLayout.addWidget(self.label)
        
        # cmj plot
        self.figure = plt.Figure(figsize = (12,16))
        self.canvas = FigureCanvas(self.figure)
        self.leftLayout.addWidget(self.canvas)
        
        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates = False)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        
        # define table for values
        self.tableComboBox = QComboBox()
        self.tableComboBox.addItems(["Full Results", "Average Results", "LSI Results"])
        self.tableComboBox.currentIndexChanged.connect(self.on_tablecombobox_changed)
        self.rightLayout.addWidget(self.tableComboBox)
        self.table = QTableWidget(self)
        self.rightLayout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # buttons for things, save data, quit program, eventually add back in go to home screen button
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignTop)
        
        # export data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        self.buttonLayout.addWidget(self.exportButton)
        
        # close program button
        self.closeAppButton = QPushButton("Quit Program", self)
        self.closeAppButton.clicked.connect(self.closeApp)
        self.buttonLayout.addWidget(self.closeAppButton)
        
        self.homeButton = QPushButton('Return to Home', self)
        self.homeButton.clicked.connect(self.returnToHome)
        self.buttonLayout.addWidget(self.homeButton)
        
        self.topLayout.addLayout(self.buttonLayout)
        
        # column selection
        self.columnSelectionPrompt()
        
        # for dropping
        self.setAcceptDrops(True)
    
    # custom function for user inputs
    def get_user_inputs(self):
        # input for participant's body mass
        pt_mass_lb, ok1 = QInputDialog.getDouble(self, "Input", "Enter Individual's Body Mass (pounds)- This must be accurate:", decimals = 2)
        if ok1:
            pt_mass_kg = pt_mass_lb / 2.2046
            self.pt_mass = pt_mass_kg
        else:
            self.close()
        # input for box height
        # defaults and constants    
        default_box_height_in = 16.0

        drop_height_in, ok2 = QInputDialog.getDouble(self, "Input", "Enter Box Height (inches):", decimals = 2, value = default_box_height_in)
        if ok2:
            drop_height_cm = drop_height_in * 2.54
            drop_height_m = drop_height_cm/100
            self.drop_height = drop_height_m
        else:
            self.close()
        
    def columnSelectionPrompt(self):
        columnOptions = [chr(i) for i in range(65, 87)]
        self.fz_left_col, ok1 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Left Column from Excel file', columnOptions, 5, False)
        self.fz_right_col, ok2 = QInputDialog.getItem(self, 'Select Column', 'Select Fz Right Column from Excel file', columnOptions, 16, False)
        
        if ok1 and ok2:
            self.fz_left_col = ord(self.fz_left_col) - 65
            self.fz_right_col = ord(self.fz_right_col) - 65
        else:
            self.close()
            
    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)
        
        variable_font = QFont("Arial bold", 8)
        value_font = QFont("Arial", 8)
        
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = dataframe.iat[i,j]
                if j == 0:
                    item = QTableWidgetItem(str(value))
                    item.setFont(variable_font)
                else:
                    numeric_value = float(value)
                    item = QTableWidgetItem(f'{numeric_value:.2f}')
                    item.setFont(value_font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(i , j, item)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
    
    # actions for changing what values are displayed in the table     
    def on_tablecombobox_changed(self, index):
        if index == 0:
            self.display_table(self.outcome_dat)
        if index == 1:
            self.average_data(self.outcome_dat)
            self.display_table(self.average_dat)
        if index == 2:
            self.display_table(self.lsi_data)
    
    # actions for changing what plot is displayed
    def on_file_combobox_changed(self):
        file_key = self.fileComboBox.currentText()
        self.current_file = self.file_path_dict[file_key]
        self.processdualDropJumpfile(self.current_file)
    
    # functions for dropping new files    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                file_name = os.path.basename(file_path)[:-4]
                self.file_path_dict[file_name] = file_path
                self.processdualDropJumpfile(file_path)
                self.average_data(self.outcome_dat)
                self.get_lsi(self.average_dat)
                if self.fileComboBox.findText(file_name) == -1:
                    self.fileComboBox.addItem(file_name)
                self.fileComboBox.setCurrentText(file_name)
                self.current_file = file_path
                self.on_tablecombobox_changed(0)
                self.drop_count = self.drop_count + 1
                
        if self.drop_count >0:
            self.average_dat = self.average_data(self.outcome_dat)
    
    # now processing a dual plate drop jump file
    def processdualDropJumpfile(self, file_path):
        # constants
        sf = 1000
        pt_mass = self.pt_mass
        pt_weight = pt_mass * 9.81
        bodymass = pt_mass
        drop_height = self.drop_height
        box_height = drop_height
        impact_velo = np.sqrt(2 * 9.81 * drop_height) * -1
        outcome_dat = self.outcome_dat
        
        # pull file name and time of creation
        file_name = os.path.basename(file_path)[:-4]
        
        # read in data and define force columns
        dat = pd.read_csv(file_path)
        fz_left = dat.iloc[:, self.fz_left_col]
        fz_right =  dat.iloc[:, self.fz_right_col]
        fz_total = fz_left + fz_right
        
        # calculate time
        trial_len = len(fz_total)
        trial_time = trial_len/sf
        time_s = np.linspace(start = 0, stop = trial_time, num = trial_len)
        
        # find ground contact
        ground_contact = 500
        while fz_total[ground_contact] < 30:
            ground_contact = ground_contact + 1
        time_ground_contact_s = time_s[ground_contact]
        
        # takeoff calculation
        takeoff = ground_contact + 1
        while fz_total[takeoff] > 30:
            takeoff = takeoff + 1
        time_takeoff_s = time_s[takeoff]
        
        # land calculation
        land = takeoff + 250
        while fz_total[land] < 30:
            land = land + 1
        time_land_s = time_s[land]
        
        # end land calculation
        end_land = land+200
        while fz_total[end_land] > pt_weight:
            end_land = end_land + 1
        while fz_total[end_land] < pt_weight:
            end_land = end_land -1
        # sanity check
        if end_land > land:
            end_land = end_land
        else:
            end_land = land+500
        time_end_land_s = time_s[end_land]
        
        # initial crop of arays from ground contact to end landing
        fz_total_cropped = fz_total[ground_contact:end_land]
        fz_net_cropped = fz_total_cropped - pt_weight # net (vGRF - pt weight)
        time_cropped_s = time_s[ground_contact:end_land]
        
        # calculate acceleration
        accel = np.array(fz_net_cropped / bodymass)
        
        # calculate velocity with a custom function, this is because
        # int_cumptraz no longer takes an initial argument (e.g., impact velo)
        # and we are not really interested in the drop phase velocity
        velo = [0] * len(accel) # empty array of 0s length of accel array
        velo[0] = impact_velo # set first value to impact velocity
        # loop that performs cumulative integration on the cropped arays
        for i in range(1, len(accel)):
            velo[i] = accel[i] * (time_cropped_s[i] - time_cropped_s[i-1]) + velo[i-1]
        # make sure velocity is an array and not a list
       # print(velo)
        velo = np.array(velo)
        #print(len(velo))
        
        # now we can calculate phases
        # concnetric based on when velocity crosses 0
        start_concentric = 1
        while velo[start_concentric] < 0:
            start_concentric = start_concentric + 1
        time_cropped_at_start_concentric_s = time_cropped_s[start_concentric]
        
        # get indices for time in the cropped array
        time_cropped_takeoff_index = np.where(time_cropped_s == time_takeoff_s)[0][0]
        time_cropped_land_index = np.where(time_cropped_s == time_land_s)[0][0]
        time_cropped_end_land_index = len(velo) # for now, end of landing phase is the lenght of velo
        
        # lastly, full time array at start concentric
        full_index_at_start_concentric = np.where(time_s == time_cropped_at_start_concentric_s)[0][0]
        time_s_at_start_concentric = time_s[full_index_at_start_concentric]
        
        ##### Phase Calculations
        # total force
        ecc_fz_total = fz_total[ground_contact:full_index_at_start_concentric]
        con_fz_total = fz_total[full_index_at_start_concentric:takeoff]
        land_fz_total = fz_total[land:end_land]
        positive_fz_total = fz_total[ground_contact:takeoff]
        
        # left force
        ecc_fz_left = fz_left[ground_contact:full_index_at_start_concentric]
        con_fz_left = fz_left[full_index_at_start_concentric:takeoff]
        land_fz_left = fz_left[land:end_land]
        positive_fz_left = fz_left[ground_contact:takeoff]
        
        # right force
        ecc_fz_right = fz_right[ground_contact:full_index_at_start_concentric]
        con_fz_right = fz_right[full_index_at_start_concentric:takeoff]
        land_fz_right = fz_right[land:end_land]
        positive_fz_right = fz_right[ground_contact:takeoff]    
        
        # velocity arrays
        ecc_velo = velo[0:start_concentric]
        con_velo = velo[start_concentric:time_cropped_takeoff_index]
        land_velo = velo[time_cropped_land_index:time_cropped_end_land_index]
        
        # power arrays 
        ecc_power = ecc_velo * ecc_fz_total
        con_power = con_velo * con_fz_total
        land_power = land_velo * land_fz_total
        
        ##### Outcomes start here
        # power outcomes
        ecc_peak_power = ecc_power.min()
        ecc_mean_power = ecc_power.mean()
        con_peak_power = con_power.max()
        con_mean_power = con_power.mean()
        land_peak_power = land_power.min()
        land_mean_power = land_power.mean()
        
        # Total Kinetic Phase Specific Outcomes
        # eccentric 
        total_ecc_peak_force_n = ecc_fz_total.max()
        total_ecc_peak_force_nkg = total_ecc_peak_force_n/bodymass
        total_ecc_mean_force_n = ecc_fz_total.mean()
        total_ecc_mean_force_nkg = total_ecc_mean_force_n/bodymass
        total_ecc_impulse = int_trapz(ecc_fz_total)/sf
            
        # concentric
        total_con_peak_force_n = con_fz_total.max()
        total_con_peak_force_nkg = total_con_peak_force_n/bodymass
        total_con_mean_force_n = con_fz_total.mean()
        total_con_mean_force_nkg = total_con_mean_force_n/bodymass
        total_con_impulse = int_trapz(con_fz_total)/sf
        
        # positive impulses
        total_positive_impulse = int_trapz(positive_fz_total)/sf
        left_positive_impulse = int_trapz(positive_fz_left)/sf
        right_positive_impulse = int_trapz(positive_fz_right)/sf

        # landing
        total_land_peak_force_n = land_fz_total.max()
        total_land_peak_force_nkg = total_land_peak_force_n/bodymass
        total_land_mean_force_n = land_fz_total.mean()
        total_land_mean_force_nkg = total_land_mean_force_n/bodymass
        total_land_impulse = int_trapz(land_fz_total)/sf
        
        # Left Leg Phase Specific Outcomes
        # eccentric 
        left_ecc_peak_force_n = ecc_fz_left.max()
        left_ecc_peak_force_nkg = left_ecc_peak_force_n/bodymass
        left_ecc_mean_force_n = ecc_fz_left.mean()
        left_ecc_mean_force_nkg = left_ecc_mean_force_n/bodymass
        left_ecc_impulse = int_trapz(ecc_fz_left)/sf
        
        # concentric
        left_con_peak_force_n = con_fz_left.max()
        left_con_peak_force_nkg = left_con_peak_force_n/bodymass
        left_con_mean_force_n = con_fz_left.mean()
        left_con_mean_force_nkg = left_con_mean_force_n/bodymass
        left_con_impulse = int_trapz(con_fz_left)/sf
        
        # landing
        left_land_peak_force_n = land_fz_left.max()
        left_land_peak_force_nkg = left_land_peak_force_n/bodymass
        left_land_mean_force_n = land_fz_left.mean()
        left_land_mean_force_nkg = left_land_mean_force_n/bodymass
        left_land_impulse = int_trapz(land_fz_left)/sf
        
        # Right Leg Phase Specific Outcomes
        # eccentric 
        right_ecc_peak_force_n = ecc_fz_right.max()
        right_ecc_peak_force_nkg = right_ecc_peak_force_n/bodymass
        right_ecc_mean_force_n = ecc_fz_right.mean()
        right_ecc_mean_force_nkg = right_ecc_mean_force_n/bodymass
        right_ecc_impulse = int_trapz(ecc_fz_right)/sf
        
        # concentric
        right_con_peak_force_n = con_fz_right.max()
        right_con_peak_force_nkg = right_con_peak_force_n/bodymass
        right_con_mean_force_n = con_fz_right.mean()
        right_con_mean_force_nkg = right_con_mean_force_n/bodymass
        right_con_impulse = int_trapz(con_fz_right)/sf
            
        # landing
        right_land_peak_force_n = land_fz_right.max()
        right_land_peak_force_nkg = right_land_peak_force_n/bodymass
        right_land_mean_force_n = land_fz_right.mean()
        right_land_mean_force_nkg = right_land_mean_force_n/bodymass
        right_land_impulse = int_trapz(land_fz_right)/sf
        
        # time-constrained outcomes
        groundcontact_time_s = time_s[takeoff] - time_s[ground_contact]
        ecc_time_s = time_s_at_start_concentric - time_ground_contact_s
        con_time_s = time_takeoff_s - time_s_at_start_concentric
        flight_time_s = time_land_s - time_takeoff_s
        land_time_s = time_end_land_s - time_land_s
        
        # RFD outcomes - later
        # velocity outcomes
        con_peak_velocity = con_velo.max()
        con_mean_velocity = con_velo.mean()
        ecc_mean_velocity = ecc_velo.mean()
        land_peak_velocity = land_velo.min()
        land_mean_velocity = land_velo.mean()
    
        # perforamnce outcomes
        vto = velo[time_cropped_takeoff_index]
        jh_m = ((vto ** 2))/(9.81 * 2)   
        jh_cm = jh_m * 100
        rsi = flight_time_s/groundcontact_time_s
        
        # concatenate into a list
        values_dat = [bodymass, box_height*100, jh_cm, rsi,
                  con_peak_power, ecc_peak_power, land_peak_power,
                  con_mean_power, ecc_mean_power, land_mean_power, 
                  total_con_peak_force_n, total_con_peak_force_nkg, total_ecc_peak_force_n, 
                  total_ecc_peak_force_nkg, total_con_mean_force_n, total_con_mean_force_nkg,
                  total_ecc_mean_force_n, total_ecc_mean_force_nkg, total_land_peak_force_n,
                  total_land_peak_force_nkg,  total_land_mean_force_n, total_land_mean_force_nkg,
                  total_con_impulse, total_ecc_impulse, total_positive_impulse,
                  total_land_impulse, left_con_peak_force_n, left_con_peak_force_nkg,
                  left_ecc_peak_force_n, left_ecc_peak_force_nkg, left_con_mean_force_n,
                  left_con_mean_force_nkg, left_ecc_mean_force_n, left_ecc_mean_force_nkg,
                  left_land_peak_force_n, left_land_peak_force_nkg, left_land_mean_force_n,
                  left_land_mean_force_nkg, left_con_impulse, left_ecc_impulse,
                  left_positive_impulse, left_land_impulse, right_con_peak_force_n,
                  right_con_peak_force_nkg, right_ecc_peak_force_n, right_ecc_peak_force_nkg,
                  right_con_mean_force_n, right_con_mean_force_nkg, right_ecc_mean_force_n,
                  right_ecc_mean_force_nkg, right_land_peak_force_n, right_land_peak_force_nkg,
                  right_land_mean_force_n, right_land_mean_force_nkg, right_con_impulse,
                  right_ecc_impulse, right_positive_impulse, right_land_impulse,
                  groundcontact_time_s, ecc_time_s, con_time_s, 
                  flight_time_s, land_time_s, con_peak_velocity,
                  land_peak_velocity, land_mean_velocity, con_mean_velocity, ecc_mean_velocity, vto]
        
        values_dat_clean = [round(float(n), 3) for n in values_dat]
        values_dat_table = [round(float(n), 3) for n in values_dat]
        
        full_table_vars = list(dualplate_dropjump_vars_dict.values())
        full_table_dat = pd.DataFrame({'Variable': full_table_vars,
                                       file_name : values_dat_table})
        
        self.display_table(self.outcome_dat)
        outcome_dat[file_name] = values_dat_clean
        
        ##### Plotting
        time_at_ground_contact_s = time_s[ground_contact]
        time_at_start_concentric_s = time_s_at_start_concentric
        time_at_takeoff_s = time_s[takeoff]
        time_at_land_s = time_s[land]
        time_at_end_land_s = time_s[end_land]
        
        # for adding annotations
        annotations = {'Ground Contact': time_at_ground_contact_s,
                       'Concentric': time_at_start_concentric_s,
                       'Flight': time_at_takeoff_s,
                       'Landing': time_at_land_s+0.1}
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axvline(x = time_at_ground_contact_s, ls = ':', color = 'grey', lw = 0.4)
        ax.axvline(x = time_at_start_concentric_s, ls = ':', color = 'grey', lw = 0.4)
        ax.axvline(x = time_at_takeoff_s, ls = ":", color = 'grey', lw = 0.4)
        ax.axvline(x = time_at_land_s, ls = ":", color = 'grey', lw = 0.4)
        sns.lineplot(x = time_s[ground_contact-500:land+1000], y = fz_total[ground_contact-500:land+1000], label = 'Total', color = '#0072B2', lw = 2, ax = ax)
        sns.lineplot(x = time_s[ground_contact-500:land+1000], y = fz_left[ground_contact-500:land+1000], label = 'Left', color = '#D55E00', lw = 1, ax = ax)
        sns.lineplot(x = time_s[ground_contact-500:land+1000], y = fz_right[ground_contact-500:land+1000], label = 'Right', color = '#56B4E9', lw = 1, ax = ax)
        ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
        ax.xaxis.set_major_locator(MaxNLocator(nbins = 'auto'))
        ax.set_ylabel('Force (N)')
        ax.set_xlabel('Time (seconds)')
        ax.legend(loc = 'upper right', frameon = False)
        
        # add annotations to plot
        y_pos = ax.get_ylim()[1]*0.95
        for label, x_coord in annotations.items():
            ax.annotate(label, xy = (x_coord, y_pos), xytext = (5,5),
                        textcoords = 'offset points', ha = 'left', va = 'top',
                        fontsize = 8, fontweight = 'bold', color = 'black', rotation = -90)
        self.canvas.draw()
        self.outcome_dat = outcome_dat
        
    # calculate averages
    def average_data(self, dataframe):
        var_names = dataframe.iloc[:, 0]
        values_dat = dataframe.iloc[:,1:]
        values_dat_mean = values_dat.mean(axis = 1)
        average_dat = pd.DataFrame({'Variable': var_names,
                                    'Average': values_dat_mean})
        self.average_dat = average_dat
   
    # function to get Limb symmetry indices 
    def get_lsi(self, dataframe):
        leg_data = dataframe[dataframe['Variable'].str.contains("Left|Right")].copy()
        leg_data['leg'] = leg_data['Variable'].apply(lambda x: 'Left' if 'Left' in x else 'Right')
        leg_data['Metric'] = leg_data['Variable'].apply(lambda x: x.split(' ', 1)[1])
        leg_data_clean = leg_data[['Metric', 'leg', 'Average']]
        leg_data_wide = leg_data_clean.pivot(index = 'Metric', columns = 'leg', values = 'Average').reset_index()
        leg_data_wide["L/R LSI"]  = np.round(leg_data_wide['Left'] / leg_data_wide['Right'], 2)
        leg_data_wide['R/L LSI'] = np.round(leg_data_wide['Right'] / leg_data_wide['Left'], 2)
        self.lsi_data = leg_data_wide  
    
    # function to export data
    def exportData(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "XLSX Files (.xlsx);;All Files (*)", options = options)
        lsi_df = self.lsi_data
        average_df = self.average_dat
        outcome_df = self.outcome_dat
        if save_path:
            if not save_path.endswith('.xlsx'):
                save_path += ".xlsx"
            with pd.ExcelWriter(save_path, engine = 'xlsxwriter') as writer:
                lsi_df.to_excel(writer, sheet_name = "LSI Data", index = False)
                average_df.to_excel(writer, sheet_name = "Average Data", index = False)
                outcome_df.to_excel(writer, sheet_name = 'Individual Data', index = False)
    
    # function to return to home screen            
    def returnToHome(self):
        self.home = AnalysisSelector()
        self.home.show()
        self.close()    
    # function to close app
    def closeApp(self):
        self.close()            
        
               
# class for analysis selector (Home screen)
class AnalysisSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TUKHS Force Plate Analysis Programs")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Please select how many plates you are using.", self)
        self.label.setFont(QFont("Arial bold", 12))
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.label)
        
        desktop_width = GetSystemMetrics(0)
        desktop_height = GetSystemMetrics(1)

        splash_width = int(desktop_width * 0.5)
        splash_height = int(desktop_height * 0.5)

        width_move = int((desktop_width - splash_width) / 2)
        height_move = int((desktop_height - splash_height) / 2)

        self.setFixedSize(splash_width, splash_height)
        self.move(width_move, height_move)

        # Button for Single Plate Analyses
        single_plate_button = QPushButton("Single Force Plate", self)
        single_plate_button.setFont(QFont("Arial bold", 16))
        single_plate_button.clicked.connect(self.show_single_plate_selection)
        self.layout.addWidget(single_plate_button)

        # Button for Dual Plate Analyses
        dual_plate_button = QPushButton("Dual Force Plates", self)
        dual_plate_button.setFont(QFont('Arial bold', 16))
        dual_plate_button.clicked.connect(self.show_dual_plate_selection)
        self.layout.addWidget(dual_plate_button)
        
    # functions for selecting how many platess
    def show_single_plate_selection(self):
        self.single_plate_window = SinglePlateSelectionWindow()
        self.single_plate_window.show()
        self.close()
    
    def show_dual_plate_selection(self):
        self.dual_plate_window = DualPlateSelectionWindow()
        self.dual_plate_window.show()
        self.close()

class SinglePlateSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Single Plate Test Options")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Please select an analysis to perform.", self)
        self.label.setFont(QFont("Arial bold", 12))
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.label)
        
        desktop_width = GetSystemMetrics(0)
        desktop_height = GetSystemMetrics(1)

        splash_width = int(desktop_width * 0.5)
        splash_height = int(desktop_height * 0.5)

        width_move = int((desktop_width - splash_width) / 2)
        height_move = int((desktop_height - splash_height) / 2)

        self.setFixedSize(splash_width, splash_height)
        self.move(width_move, height_move)
        
        single_plate_cmj_button = QPushButton("Bilateral CMJ", self)
        single_plate_cmj_button.setFont(QFont("Arial bold", 14))
        single_plate_cmj_button.clicked.connect(self.run_single_plate_cmj_analysis)
        self.layout.addWidget(single_plate_cmj_button)
        
        single_plate_slj_button = QPushButton("Unilateral CMJ", self)
        single_plate_slj_button.setFont(QFont("Arial bold", 14))
        single_plate_slj_button.clicked.connect(self.run_single_plate_slj_analysis)
        self.layout.addWidget(single_plate_slj_button)
             
        single_plate_unilateral_drop_button = QPushButton("Unilateral Drop Landing", self)
        single_plate_unilateral_drop_button.setFont(QFont("Arial bold", 14))
        single_plate_unilateral_drop_button.clicked.connect(self.run_single_plate_sldrop_analysis)
        self.layout.addWidget(single_plate_unilateral_drop_button)
        
        single_plate_unilateral_drop_jump_button = QPushButton("Unilateral Drop Jump", self)
        single_plate_unilateral_drop_jump_button.setFont(QFont("Arial bold", 14))
        single_plate_unilateral_drop_jump_button.clicked.connect(self.run_single_plate_dj_analaysis)
        self.layout.addWidget(single_plate_unilateral_drop_jump_button)
        
    # defining local functions to run actual analyses    
    def run_single_plate_cmj_analysis(self):
        self.single_plate_cmj_analysis_window = SinglePlateCMJAnalysisWindow()
        self.single_plate_cmj_analysis_window.show()
        self.close() 
        
    def run_single_plate_slj_analysis(self):
        self.single_plate_slj_analysis_window = SinglePlateSLJAnalysisWindow()
        self.single_plate_slj_analysis_window.show()
        self.close()
    
    def run_single_plate_sldrop_analysis(self):
        self.single_plate_sldrop_analysis_window = SinglePlateSLDropWindow()
        self.single_plate_sldrop_analysis_window.show()
        self.close()
        
    def run_single_plate_dj_analaysis(self):
        self.single_plate_dj_analysis_window = SinglePlateDropJumpAnalysisWindow()
        self.single_plate_dj_analysis_window.show()
        self.close()

class DualPlateSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Dual Plate Test Options")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Please select an analysis to perform.", self)
        self.label.setFont(QFont("Arial bold", 12))
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.label)
        
        desktop_width = GetSystemMetrics(0)
        desktop_height = GetSystemMetrics(1)

        splash_width = int(desktop_width * 0.5)
        splash_height = int(desktop_height * 0.5)

        width_move = int((desktop_width - splash_width) / 2)
        height_move = int((desktop_height - splash_height) / 2)

        self.setFixedSize(splash_width, splash_height)
        self.move(width_move, height_move)
        
        dual_plate_cmj_button = QPushButton("Bilateral CMJ", self)
        dual_plate_cmj_button.setFont(QFont("Arial bold", 14))
        dual_plate_cmj_button.clicked.connect(self.run_dual_plate_cmj_analysis)
        self.layout.addWidget(dual_plate_cmj_button)
        
        dual_plate_drop_button = QPushButton("Bilateral Drop Landing", self)
        dual_plate_drop_button.setFont(QFont("Arial bold", 14))
        dual_plate_drop_button.clicked.connect(self.run_dual_plate_drop_analysis)
        self.layout.addWidget(dual_plate_drop_button)
                
        dual_plate_drop_jump_button = QPushButton("Bilateral Drop Jump", self)
        dual_plate_drop_jump_button.setFont(QFont("Arial bold", 14))
        dual_plate_drop_jump_button.clicked.connect(self.run_dual_plate_drop_jump_analysis)
        self.layout.addWidget(dual_plate_drop_jump_button)
        
    def run_dual_plate_cmj_analysis(self):
        self.dual_plate_cmj_analysis_window = DualPlateCMJAnalysisWindow()
        self.dual_plate_cmj_analysis_window.show()
        self.close()
        
    def run_dual_plate_drop_analysis(self):
        self.dual_plate_drop_analysis_window = DualPlateDropLandingAnalysisWindow()
        self.dual_plate_drop_analysis_window.show()
        self.close()
    
    def run_dual_plate_drop_jump_analysis(self):
        self.dual_plate_drop_jump_analysis_window = DualPlateDropJumpAnalysisWindow()
        self.dual_plate_drop_jump_analysis_window.show()
        self.close()
    
            


# defining main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    app.setStyle('FusionDark')
    
    # now defining logic for selection of program to run
    selection = AnalysisSelector()
    selection.show()
    sys.exit(app.exec_())
