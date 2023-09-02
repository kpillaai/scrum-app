from RoleType import RoleType
from Task import Task


class User:
    next_id = 1

    def __int__(self, name: str, role: RoleType, email: str, phone_number: str):
        self.name = name
        self.id = User.next_id  # unique id for each User
        User.next_id += 1
        self.role = role  # from RoleType, either ADMIN or MEMBER
        self.email = email
        self.phone_number = phone_number
        self.task_dict = {}  # dict used to store tasks this user has contributed to, key is task.id, value is hours

    def add_task(self, task: Task) -> None:
        """
        Adds a task to this User and adds it to the User's task_dict
        :param task: Task the User is working on
        :return: None
        """
        if self.task_dict[task.id] is not None:
            pass
        else:
            self.task_dict[task.id] = 0

    def update_hours(self, task: Task, hours: int) -> None:
        """
        Update the number of hours the User has spent working on the assigned Task
        :param task: Task the User is assigned to
        :param hours: number of hours the User contributed
        :return: None
        """
        self.task_dict[task.id] += hours
