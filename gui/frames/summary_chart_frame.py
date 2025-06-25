# new file: gui/frames/summary_chart_frame.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configure Matplotlib style ONCE when the module is imported
plt.style.use("dark_background")


class SummaryChartFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self, text="Category Summary", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=10)

        # Create a figure and a subplot with a matching dark background
        self.figure = plt.Figure(figsize=(5, 4), dpi=100, facecolor="#2B2B2B")
        self.ax = self.figure.add_subplot(111, facecolor="#2B2B2B")

        # Create a canvas to embed the chart in our CTk window
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        self.update_chart(None)  # Initialize with an empty state

    def update_chart(self, summary_df):
        """Clears the old chart and draws a new one with the provided summary data."""
        self.ax.clear()

        if summary_df is None or summary_df.empty:
            self.ax.text(
                0.5, 0.5, "No data to visualize", ha="center", va="center", color="gray"
            )
        else:
            # Prepare colors based on values (positive=green, negative=red)
            colors = ["#27AE60" if x >= 0 else "#C0392B" for x in summary_df["Total"]]

            # Create the horizontal bar chart
            self.ax.barh(summary_df["Category"], summary_df["Total"], color=colors)

            # Style the chart axes and grid for better readability
            self.ax.tick_params(axis="y", colors="white", labelsize=9)
            self.ax.tick_params(axis="x", colors="white", labelsize=9)
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["left"].set_color("gray")
            self.ax.spines["bottom"].set_color("gray")
            self.ax.grid(
                axis="x", color="gray", linestyle="--", linewidth=0.5, alpha=0.5
            )
            self.ax.xaxis.set_major_formatter("{x:,.0f}")

        # Ensure the layout is tight to prevent labels from being cut off
        self.figure.tight_layout(pad=1.5)

        # Redraw the canvas to show the new chart
        self.canvas.draw()
