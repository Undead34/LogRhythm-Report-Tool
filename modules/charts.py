import chartify


class Charts():
    def __init__(self) -> None:
        pass

    def pie(self):
        # Generate example data
        data = chartify.examples.example_data()

        # Sum price grouped by date
        # Move 'date' from index to column
        price_by_date = data.groupby("date")["total_price"].sum().reset_index()

        # Plot the data
        ch = chartify.Chart(blank_labels=True, x_axis_type="datetime")
        ch.set_title("Line charts")
        ch.set_subtitle(
            "Plot two numeric values connected by an ordered line.")
        ch.plot.line(
            # Data must be sorted by x column
            data_frame=price_by_date.sort_values("date"),
            x_column="date",
            y_column="total_price",
        )

        ch.save("char.png", "png")
