import math
from pydantic import BaseModel

class GroupedAnswerInfo(BaseModel):
    distance: float
    count_correct: int
    count_total: int

def calculate_score(answers_grouped_by_distance: list[GroupedAnswerInfo], d0: float = 20.0, gamma: float = 0.7) -> float:
    """
    Calculate the score (resolution) for a glyph (rounded to 2 decimal places), based on the accuracy of answers at different distances.

    Args:
        answers_grouped_by_distance (list[GroupedAnswerInfo]): A list of GroupedAnswerInfo objects, where each object has the following attributes:
            - distance (float): The distance of the answers in this group
            - count_correct (int): The number of correct answers in this group
            - count_total (int): The total number of answers in this group
    """

    # Sort the groups by distance (ascending)
    answers_grouped_by_distance = sorted(answers_grouped_by_distance, key=lambda x: x.distance)

    accuracy_per_distance = [ 
        (group.count_correct / group.count_total) if group.count_total > 0 else 0.0
        for group in answers_grouped_by_distance
    ]

    
    sum_temp = 0.0
    for i in range(len(accuracy_per_distance)):
        sum_temp = sum_temp + accuracy_per_distance[i] + (accuracy_per_distance[i+1] if i < len(accuracy_per_distance) - 1 else 0.0)
    sum_temp = (1.0/2.0) * sum_temp * math.log(1/gamma)
    area_under_curve = (1.0/math.log(2)) * (sum_temp + math.log(100.0/d0))

    resolution = math.pow(2, area_under_curve)

    return round(resolution, 2)