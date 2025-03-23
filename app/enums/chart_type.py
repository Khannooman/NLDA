from enum import Enum

class ChartType(Enum):
    BOX_PLOT = 'box_plot'
    HISTOGRAM = 'histogram'
    SCATTER_PLOT = 'scatter_plot'
    LINE_PLOT = 'line_plot'
    HEATMAP = 'heatmap'
    PIE_CHART = 'pie_chart'
    BAR_CHART = 'bar_chart'
    LINE_CHART = 'line_chart'
    DONUT_CHART = 'donut_chart'
    AREA_CHART = 'area_chart'
    NUMBER_CARD = 'number_card'
    TABLE = 'table'