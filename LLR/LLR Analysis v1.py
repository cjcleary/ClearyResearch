import sys
import os
import numpy as np
import pandas as pd
import shutil
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
import qdarktheme
from scipy.signal import butter, filtfilt

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

class LLRAnalysis(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()

        # Variables for signal, corrected signal, baseline, and selected range
        self.signal = None
        self.updated_signal = None
        self.baseline = None
        self.selected_range = [0, 1]  # Default to the first 1 second
        self.filename = ''
        self.sample_rate = 2000  # Hz
        self.ax = None  # Axis for plotting
        self.files_in_directory = []
        self.clicked = False  # Flag to prevent multiple clicks
        
        # initialize dataframe for saving MVIC values to
        self.mvic_dat = pd.DataFrame()

        self.rect_width = 2000  # Fixed rectangle width (1 second at 2000Hz)
        self.save_directory = ''  # Directory for saving the corrected signals

    def initUI(self):
        self.setWindowTitle("Baseline Correction")
        self.setGeometry(100, 100, 1600, 800)

        # Main widget layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QVBoxLayout(self.centralWidget)

        # Layout for buttons (horizontally arranged)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)  # Adjust the spacing between buttons (in pixels)

        # Top section with buttons
        self.selectDirButton = QPushButton("Select Input Folder")
        self.selectDirButton.clicked.connect(self.load_data)
        button_layout.addWidget(self.selectDirButton)

        # Add Save Directory Button
        self.saveDirButton = QPushButton("Select Output Folder")
        self.saveDirButton.clicked.connect(self.select_save_directory)
        button_layout.addWidget(self.saveDirButton)

        # Add Save Button
        self.saveButton = QPushButton("Next File")
        self.saveButton.clicked.connect(self.save_corrected_signal)
        button_layout.addWidget(self.saveButton)

        # Add Redo Selection Button
        self.redoButton = QPushButton("Redo Selection")
        self.redoButton.clicked.connect(self.redo_selection)
        button_layout.addWidget(self.redoButton)
        
        # export and save data button
        self.exportButton = QPushButton("Save Data", self)
        self.exportButton.clicked.connect(self.exportData)
        button_layout.addWidget(self.exportButton)
        
        # close app button
        self.closeButton = QPushButton('Close', self)
        self.closeButton.clicked.connect(self.closeApp)
        button_layout.addWidget(self.closeButton)
        
        # button container
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setContentsMargins(150, 0, 150, 0)
        layout.addWidget(button_container)

        # Left section (table for displaying files)
        self.tableLayout = QVBoxLayout()  
        self.table = QTableWidget(self)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Files to Analyze"])
        self.tableLayout.addWidget(self.table)
        self.table.verticalHeader().setVisible(False)
        
        # Adjust table width based on content
        self.table.setColumnWidth(0, 100)  # Adjust column width (can be changed to fit the file names)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setFixedWidth(140)  # You can adjust this value to make it smaller
        # Alternatively, use self.table.setMaximumWidth(300) to limit the maximum width

        # Adjust layout properties: Adjust spacing and set stretch factor
        self.tableLayout.setSpacing(0)  # Adjust the spacing between the table and other widgets
        self.tableLayout.setContentsMargins(0, 0, 0, 0)  # Adjust margins around the table

        # Stretch factor for the table layout: Keep it smaller compared to the right section
        self.tableLayout.setStretchFactor(self.table, 0) 
        
        # Right section (plots)
        self.rightLayout = QVBoxLayout()  
        self.leftLayout = QVBoxLayout()  # Layout for the plots on the right
        h_layout = QHBoxLayout()  # Horizontal layout to combine table and plot
        h_layout.addLayout(self.tableLayout)  # Table takes less space
        h_layout.addLayout(self.rightLayout, stretch=4)  # Plots take more space
        layout.addLayout(h_layout)

        # Add plot canvas for original and corrected signals
        self.figure1 = plt.Figure(figsize=(8, 6))  # Smaller figure size
        self.canvas1 = FigureCanvas(self.figure1)
        self.rightLayout.addWidget(self.canvas1)  # Place canvas1 on the right layout

        self.figure2 = plt.Figure(figsize=(8, 6))  # Smaller figure size
        self.canvas2 = FigureCanvas(self.figure2)
        self.rightLayout.addWidget(self.canvas2)  # Place canvas2 on the right layout

    def load_data(self):
        # Open file dialog to select a directory
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            # Filter files containing "LLR" in the filename
            self.files_in_directory = [f for f in os.listdir(folder) if 'LLR' in f]
            self.update_file_table()

            if self.files_in_directory:
                self.filename = os.path.join(folder, self.files_in_directory[0])  # Load the first file
                self.basename = self.files_in_directory[0]
                self.signal = np.loadtxt(self.filename, usecols = 0) # Assuming signal data is in the first column
                self.updated_signal = self.signal.copy()
                self.plot_original_signal()

    def select_save_directory(self):
        # Open file dialog to select a directory to save corrected files
        folder = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if folder:
            self.save_directory = folder
        else:
            # Default to a subdirectory in the current directory
            base_dir = os.path.dirname(self.filename)
            self.save_directory = os.path.join(base_dir, "Baseline Corrected Automatic")
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

    def update_file_table(self):
        # Update the table widget with the filtered files
        self.table.setRowCount(len(self.files_in_directory))
        for i, file in enumerate(self.files_in_directory):
            self.table.setItem(i, 0, QTableWidgetItem(file))
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.resizeColumnsToContents()

    def plot_original_signal(self):
        # Clear the previous axes and create a new one for the new signal
        self.figure1.clf()  # Clear the entire figure (removes all axes)
        self.ax = self.figure1.add_subplot(111)  # Create a new axis

        # Plot the original signal on canvas1
        time = np.linspace(0, len(self.signal) / self.sample_rate, len(self.signal))
        self.ax.plot(time, self.signal, color="red")
        self.ax.set_title(f"Original Signal - {self.basename}")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force (N)")
        self.ax.xaxis.set_major_locator(MaxNLocator(integer = False, prune = 'both', ))
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
        self.figure1.tight_layout()
        self.canvas1.draw()

        # Disconnect any previous event handler
        if hasattr(self, 'cid'):
            self.figure1.canvas.mpl_disconnect(self.cid)

        # Set up the cursor behavior (click to select baseline) and ensure only one click
        self.cid = self.figure1.canvas.mpl_connect('button_press_event', self.on_click)
        self.clicked = False  # Flag to track if the plot has been clicked
        
        self.figure2.clf()
        self.canvas2.draw()
 
    def on_click(self, event):
        if self.clicked:  # If clicked once, do nothing
            return
        if event.inaxes != self.ax:
            return
        # Get the clicked x position and calculate the selected range (0.5 seconds wide)
        x_click = event.xdata
        x_start = x_click 
        x_end = x_click + 0.5  # 0.5 second wide (based on sample rate of 2000Hz)

        # Ensure the selected range does not go out of bounds
        if x_end > len(self.signal) / self.sample_rate:
            x_end = len(self.signal) / self.sample_rate

        self.selected_range = [x_start, x_end]

        # Clear the plot and redraw the signal with the rectangle
        self.ax.clear()
        self.ax.plot(np.linspace(0, len(self.signal) / self.sample_rate, len(self.signal)), self.signal, color= 'red')
        self.ax.axvspan(x_start, x_end, color='grey', alpha=0.2)  # Show the 0.5-second wide rectangle
        self.ax.set_title(f"Original Signal - {self.basename}")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force (N)")
        self.ax.xaxis.set_major_locator(MaxNLocator(integer = False, prune = 'both'))
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
        self.canvas1.draw()

        # Calculate the baseline from the selected range
        start_idx = int(x_start * self.sample_rate)
        end_idx = int(x_end * self.sample_rate)
        self.baseline = np.mean(self.signal[start_idx:end_idx])
        #print(f'Size of selected baseline = {len(self.signal[start_idx:end_idx])}')
        #print(f"Baseline value: {self.baseline}")

        # Subtract the baseline from the original signal to get the corrected signal
        self.updated_signal = self.signal - self.baseline
        self.plot_corrected_signal()
        self.clicked = True  # Mark the plot as clicked

    def redo_selection(self):
        # Clear the second figure and reset the corrected signal
        self.figure2.clear()
        self.canvas2.draw()
        self.updated_signal = self.signal.copy()  # Reset corrected signal
        self.clicked = False  # Allow the user to click again
    
    def plot_corrected_signal(self):
        # Plot the baseline-corrected signal on canvas2
        # filter parameters
        fc = 10
        nyf = 0.5 * self.sample_rate
        order = 2 ## zero lag filter, applied twice so needs to be 2 to make a 4th order filter
        cn = fc/nyf 
        b, a = butter(N = order, Wn = cn, btype = 'low', analog = False)
        self.filtered_signal = filtfilt(b, a, self.updated_signal)
        
        ## calculate MVIC
        mvic_array = []
        epoch_dur = 0.25
        epoch_samples = int(epoch_dur * self.sample_rate)
        
        # loop over the force array, calculating the mean of all 250 ms
        for start_idx in range(len(self.filtered_signal) - epoch_samples):
            end_idx = start_idx + epoch_samples
            epoch_avg = np.mean(self.filtered_signal[start_idx:end_idx])
            mvic_array.append(epoch_avg)
            
        mvic = max(mvic_array) # pull the max value of the possible mvics 
        self.mvic = mvic
        mvic_idx = mvic_array.index(mvic)
        mvic_start_time = mvic_idx / self.sample_rate
        mvic_end_time = mvic_start_time + epoch_dur
        annotation_x = (mvic_start_time + mvic_end_time) / 2
        annotation_y = max(self.filtered_signal) * 0.5
        
        # plotting 
        time = np.linspace(0, len(self.updated_signal) / self.sample_rate, len(self.updated_signal))
        ax = self.figure2.add_subplot(111)
        ax.clear()
        ax.plot(time, self.updated_signal, color="blue", ls = '--', lw = 0.4)
        ax.plot(time, self.filtered_signal, color = 'black', lw = 2.0)
        ax.axvspan(mvic_start_time, mvic_end_time, color = 'orange', alpha = 0.3)
        ax.set_title(f"Corrected/Filtered Signal - {self.basename}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Force (N)")
        ax.annotate(f'MVIC\n{mvic:.2f} N',
                    xy = (annotation_x, annotation_y),
                    xytext =  (annotation_x, annotation_y + 0.02 * max(self.filtered_signal)),
                    ha = 'center', fontsize = 6, color = 'black')
        ax.xaxis.set_major_locator(MaxNLocator(integer = False, prune = 'both'))
        ax.yaxis.set_major_locator(MaxNLocator(nbins = 'auto', prune = 'both'))
        self.figure2.tight_layout()
        self.canvas2.draw()
        
        new_dat = pd.DataFrame([{'Filename': self.basename,
                                      'MVIC': mvic}])
        self.mvic_dat = pd.concat([self.mvic_dat, new_dat], ignore_index=True)
        #print(self.mvic_dat)
        
    def save_corrected_signal(self):
        # Save the corrected signal to a CSV file
        if self.save_directory:
            save_path = os.path.join(self.save_directory, f"{os.path.splitext(self.basename)[0]}_corrected.csv")
            np.savetxt(save_path, self.updated_signal, delimiter=',', fmt = '%0.8f')
           # print(f"Saved baseline corrected signal to: {save_path}")

            # Move the original (uncorrected) file to "0- Analyzed MVICs"
            analyzed_dir = os.path.join(os.path.dirname(self.filename), "0- Analyzed MVICs")
            if not os.path.exists(analyzed_dir):
                os.makedirs(analyzed_dir)
            shutil.move(self.filename, os.path.join(analyzed_dir, self.basename))
            #print(f"Moved original file to: {analyzed_dir}")

            # Load the next file from the list
            self.files_in_directory.pop(0)  # Remove the current file from the list
            if self.files_in_directory:
                self.filename = os.path.join(os.path.dirname(self.filename), self.files_in_directory[0])  # Load the next file
                self.basename = self.files_in_directory[0]
                self.signal = np.loadtxt(self.filename, usecols = 0) # Load the next signal
                self.updated_signal = self.signal.copy()
                self.plot_original_signal()
                self.update_file_table()
            else: # correction for in case all files are analyzed
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Analysis Completed")
                msg_box.setText("All files have been analyzed in selected folder!\nPress OK to save data and close program.")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.buttonClicked.connect(self.closeApp)
                msg_box.exec()
        else:
            print("Save directory is not selected!")
            
    def exportData(self):

        save_path, _ = QFileDialog.getSaveFileName(self, 
                                                "Save MVIC Data", 
                                                "", 
                                                "CSV Files (*.csv);;All Files (*)")
        # Check if a save path is provided
        if save_path:
            # Check if the file exists, and append if it does
            if os.path.exists(save_path):
                existing_data = pd.read_csv(save_path)
                combined_data = pd.concat([existing_data, self.vmci_dat], ignore_index=True)
                combined_data = combined_data.drop_duplicates(subset = 'Filename', keep = 'last')
                combined_data.to_csv(save_path, mode='a', header=False, index=False)  # Append to CSV without header
                print(f"Data appended to {save_path}")
            else:
                self.mvic_dat = self.mvic_dat.drop_duplicates(subset = 'Filename', keep = 'last')
                self.mvic_dat.to_csv(save_path, index=False)  # Save as new CSV if file doesn't exist
                print(f"Data exported to {save_path}")
                
    def closeApp(self):
        self.exportData()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = LLRAnalysis()
    window.show()
    sys.exit(app.exec())
