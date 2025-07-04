# new file: gui/frames/summary_chart_frame.py
import customtkinter as ctk

# Configure matplotlib backend for compatibility with frozen executables
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Force TkAgg backend for compatibility
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, charts will be disabled")

# Configure Matplotlib style ONCE when the module is imported
if MATPLOTLIB_AVAILABLE:
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

        if MATPLOTLIB_AVAILABLE:
            # Create a figure and a subplot with a matching dark background
            self.figure = plt.Figure(figsize=(5, 4), dpi=100, facecolor="#2B2B2B")
            self.ax = self.figure.add_subplot(111, facecolor="#2B2B2B")

            # Create a canvas to embed the chart in our CTk window
            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
            self.update_chart(None)  # Initialize with an empty state
        else:
            # Fallback when matplotlib is not available
            self.fallback_label = ctk.CTkLabel(
                self,
                text="Charts not available\n(matplotlib not installed)",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            self.fallback_label.grid(row=1, column=0, sticky="nsew")

    def update_chart(self, summary_df):
        """Clears the old chart and draws a new one with the provided summary data."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.ax.clear()

        if summary_df is None or summary_df.empty:
            self.ax.text(
                0.5, 0.5, "No data to visualize", ha="center", va="center", color="gray"
            )
        else:
            # Define a color palette for different categories
            color_palette = [
                "#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
                "#1ABC9C", "#E67E22", "#34495E", "#F1C40F", "#E91E63",
                "#00BCD4", "#FF5722", "#4CAF50", "#FF9800", "#9C27B0",
                "#607D8B", "#795548", "#FFEB3B", "#2196F3", "#FFC107"
            ]

            # Use absolute values for bar heights
            bar_heights = summary_df["Total"].abs()

            # Assign colors to categories (cycle through palette if more categories than colors)
            colors = [color_palette[i % len(color_palette)] for i in range(len(summary_df))]

            # Create the vertical bar chart with different colors for each category
            self.ax.bar(range(len(summary_df)), bar_heights, color=colors)
            self.ax.set_ylabel("Total (Absolute)")
            self.ax.set_title("Total by Category")

            # Remove x-axis labels and ticks since we'll use a legend
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_xlabel("")  # Remove x-axis label

            # Style the chart axes and grid for better readability
            self.ax.tick_params(axis="y", colors="white", labelsize=9)
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["left"].set_color("gray")
            self.ax.spines["bottom"].set_color("gray")
            self.ax.grid(
                axis="y", color="gray", linestyle="--", linewidth=0.5, alpha=0.5
            )
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

            # Create legend with category names and colors
            legend_elements = []
            for i, category in enumerate(summary_df["Category"]):
                legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=colors[i], label=category))

            # Add legend below the chart
            self.ax.legend(
                handles=legend_elements,
                loc='upper center',
                bbox_to_anchor=(0.5, -0.15),
                ncol=min(3, len(summary_df)),  # Max 3 columns for better layout
                fontsize=8,
                frameon=False,
                labelcolor='white'
            )

        # Ensure the layout is tight to prevent labels from being cut off
        self.figure.tight_layout(pad=2.0)  # Increased padding for legend

        # Redraw the canvas to show the new chart
        self.canvas.draw()

    def __del__(self):
        """Cleanup matplotlib resources."""
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'figure'):
            try:
                plt.close(self.figure)
            except Exception:
                pass
