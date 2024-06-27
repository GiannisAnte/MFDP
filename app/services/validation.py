from typing import List, Tuple, Any


class Validation:
    @staticmethod
    def validate(data: List[Any]) -> Tuple:
        valid_data = []
        invalid_data = []

        for item in data:
            if Validation.is_valid(item):
                valid_data.append(item)
            else:
                invalid_data.append(item)

        return valid_data, invalid_data

    @staticmethod
    def is_valid(data_item: Any) -> bool:
        # isinstance(data_item, dict)
        ...
