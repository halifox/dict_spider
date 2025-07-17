import csv
import os


class CsvPipeline:
    def open_spider(self, spider):
        fn = f'{spider.name}.csv'
        file_exists = os.path.isfile(fn)
        self.file = open(fn, 'a', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=[
            'dict_id', 'dict_pid', 'dict_name', 'dict_innerid', 'dict_time',
            'dict_downcount', 'dict_exps', 'dict_tiers'
        ])
        if not file_exists or os.path.getsize(fn) == 0:
            self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow(item)
        self.file.flush()
        os.fsync(self.file.fileno())
        return item
