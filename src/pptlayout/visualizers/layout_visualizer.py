import matplotlib.patches as patches
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec

sns.set_theme(style="whitegrid")


def layout_visualizer(
    ax: Axes,
    slide_width: int | float,
    slide_height: int | float,
    slide_layout: dict,
) -> None:
    ax.set_xlim(0, slide_width)
    ax.set_ylim(0, slide_height)
    ax.set_aspect("equal", adjustable="box")
    ax.invert_yaxis()  # Flip the y-axis to match slide coordinate systems

    for shape in slide_layout["shapes"]:
        _draw_shape(ax, shape)

    ax.axis("on")  # Hide axes for a cleaner slide look


def _draw_shape(ax: Axes, shape: dict) -> None:
    left = shape["left"]
    top = shape["top"]
    width = shape["width"]
    height = shape["height"]
    # text = shape.get("text", "")
    type = shape["shape_type"]
    color = "lightblue"  # Default color for visualization

    # Draw rectangle representing the shape
    rect = patches.Rectangle(
        (left, top),
        width,
        height,
        linewidth=1,  # Increase the line width for visibility
        edgecolor="black",  # Ensure the border color is black
        facecolor=color,
        alpha=0.6,  # Keep the fill slightly transparent
    )
    ax.add_patch(rect)

    # Add text inside the rectangle
    ax.text(
        left + width / 2,
        top + height / 2,
        type,
        color="black",
        fontsize=8,
        ha="center",
        va="center",
    )


# Function to create a grid of slide visualizations
def generate_slide_grid(
    slide_data_list: list,
    slide_width: int | float,
    slide_height: int | float,
    grid_cols: int = 3,
) -> None:
    num_slides = len(slide_data_list)
    grid_rows = -(
        -num_slides // grid_cols
    )  # Calculate the number of rows (ceil division)

    fig = plt.figure(figsize=(15, 5 * grid_rows))
    grid_spec = GridSpec(grid_rows, grid_cols, figure=fig)

    for idx, slide_layout in enumerate(slide_data_list):
        row = idx // grid_cols
        col = idx % grid_cols
        ax = fig.add_subplot(grid_spec[row, col])
        layout_visualizer(ax, slide_width, slide_height, slide_layout)
        ax.set_title(f"Slide {slide_layout['slide_id']}")

    plt.tight_layout()
    plt.show()


def generate_comparison_grid(
    original_slide_data_list: list,
    revised_slide_data_list: list,
    slide_width: int | float,
    slide_height: int | float,
    grid_cols: int = 3,
) -> None:
    num_slides = len(original_slide_data_list)
    grid_rows = num_slides  # One row per slide

    # Create a grid with double the columns for comparison (one for original and one for revised)
    fig = plt.figure(figsize=(15, 5 * grid_rows))
    grid_spec = GridSpec(
        grid_rows, 2, figure=fig
    )  # Two columns per row (original and revised)

    for idx, (original_slide, revised_slide) in enumerate(
        zip(original_slide_data_list, revised_slide_data_list)
    ):
        row = idx  # Each row corresponds to a slide
        # Column 0 for the original slide
        ax = fig.add_subplot(grid_spec[row, 0])
        layout_visualizer(ax, slide_width, slide_height, original_slide)
        ax.set_title(f"Original Slide {original_slide['slide_id']}", fontsize=10)

        # Column 1 for the revised slide
        ax = fig.add_subplot(grid_spec[row, 1])
        layout_visualizer(ax, slide_width, slide_height, revised_slide)
        ax.set_title(f"Revised Slide {revised_slide['slide_id']}", fontsize=10)

    plt.tight_layout(pad=2)  # Adjust padding to avoid cutting off parts of the layout
    plt.show()
