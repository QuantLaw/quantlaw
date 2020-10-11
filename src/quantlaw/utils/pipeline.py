import multiprocessing


class PipelineStep:
    max_number_of_processes = max(multiprocessing.cpu_count() - 2, 1)
    chunksize = None

    def __init__(self, processes=None, execute_args=[]):
        self.processes = processes
        self.execute_args = execute_args

    def get_items(self) -> list:
        raise Exception("This function must be implemented in the subclass")

    def execute_item(self, item):
        raise Exception("This function must be implemented in the subclass")

    def execute_items(self, items):
        ctx = multiprocessing.get_context()
        processes = self.processes or self.__class__.max_number_of_processes

        if processes > 1:
            with ctx.Pool(processes) as p:
                results = p.starmap(
                    self.execute_item,
                    [(i, *self.execute_args) for i in items],
                    self.__class__.chunksize,
                )
        else:
            results = []
            for item in items:
                results.append(self.execute_item(item, *self.execute_args))

        return self.finish_execution(results)

    def execute_filtered_items(self, items, filters=None, *args, **kwargs):
        if filters:
            filtered_items = []
            for item in list(items):
                for filter_str in filters:
                    if filter_str in item:
                        filtered_items.append(item)
                        break
        else:
            filtered_items = items

        return self.execute_items(filtered_items, *args, **kwargs)

    def finish_execution(self, results):
        return results
