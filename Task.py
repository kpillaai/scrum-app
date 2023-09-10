from datetime import datetime
from TaskStatus import TaskStatus



class Task:
    next_id = 1

    def __init__(self, name: str, priority: int, estimated_effort: int, status: TaskStatus, due_date: datetime, description: str, assignee: str):
        self.name = name
        self.id = Task.next_id  # unique id for each task
        Task.next_id += 1
        self.priority = priority
        self.estimated_effort = estimated_effort
        # should a status be TODO by default?
        self.status = status  # from TaskStatus, either TODO, IN_PROGRESS or DONE
        self.start_date = datetime.today()
        self.due_date = due_date
        self.description = description
        self.assignee = assignee  # just one User per task or multiple?
        self.hours_taken = 0

        self.assignee.add_task(self)

    def update_status(self, new_status: TaskStatus) -> None:
        """
        Used to update the status of tasks as they move across the board
        :param new_status: the new status of the task
        :return: None
        """
        self.status = new_status

    def change_assignee(self, new_assignee: str) -> None:
        """
        Used to change assignee of the current task
        :param new_assignee: the new User
        :return: None
        """
        self.assignee = new_assignee
        self.assignee.add_task(self)

    def update_hours_taken(self, hours: int) -> None:
        """
        Used to update the hours spent on this Task
        :param hours: number of hours spent
        :return: None
        """
        self.hours_taken += hours

    def update_user_hours(self, hours: int) -> None:
        """
        Update the hours the User has spent on this Task
        :param hours: number of hours the User has spent
        :return: None
        """
        self.assignee.update_hours(self, hours)
        self.update_hours_taken(hours)


