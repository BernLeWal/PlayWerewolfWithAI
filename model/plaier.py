"""
Representing an AI-agent which will take part as player in Werewolve games
"""
import threading
import queue
import time


class Plaier:
    """Representing a AI-agent"""
    def __init__(self, name :str) ->None:
        self.name = name
        self.message_queue = queue.Queue()
        self.thread = threading.Thread(target=self.__worker_task__)
        self.thread.daemon = True


    def __worker_task__(self):
        while True:
            try:
                # Get message from the queu and process it
                message = self.message_queue.get(timeout=60)
                print(f"Worker processing: {message}")

                if message == "!quit":
                    break;

                time.sleep(3)   # simulate some processing

                # Signal that the task is done
                self.message_queue.task_done()

            except queue.Empty:
                # No message received within 60 seconds
                print("No new messages. Worker is waiting....")


    def start(self) ->None:
        """Start the worker thread"""
        self.thread.start()

    def add_message(self, message) ->None:
        """Put a message in the queue"""
        self. message_queue.put(message)


if __name__ == "__main__":
    plaier = Plaier("AI-Agent")
    plaier.add_message("Hi")
    plaier.add_message("Ho")
    plaier.start()
    plaier.add_message("Foo")
    plaier.add_message("Bar")
    time.sleep(20)
    plaier.add_message("!quit")
