from algorithms.gait_basic.main import SVOGaitAnalyzer

if __name__ == '__main__':
    analyzer = SVOGaitAnalyzer()
    result = analyzer.run(
        data_root_dir='/root/backend/data/test',
        file_id='2021-04-01-1-4',
        # data_root_dir='/root/backend/data/87559608-0c9d-4431-9131-18c770be22bf/',
        # file_id='uploaded',
    )
    print(result)
