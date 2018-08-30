# threads = [threading.Thread(target=download_images_partial, args=(queue,)) for i in range(n_threads)]
#
#
# for thread in threads:
#     thread.start()
# for thread in tqdm(threads):
#     thread.join()

# multiprocessing.log_to_stderr()
# logger = multiprocessing.get_logger()
# logger.setLevel(logging.INFO)

# pool = multiprocessing.Pool()  # number of processes = CPU cores available

"""
map is just like the normal map. It distributes tasks to threads, which act immediately. Wraps map_async.
"""
# pool.map(download_images_partial, catalog_partial)

"""
again like functools, imap is map but returning a lazy iterator. Results are calculated when the iterator is called.
"""

# for _ in tqdm(pool.imap(download_images_partial, catalog[250000:]), total=len(catalog[250000:]), unit=' images created'):
#     pass

"""
each apply_async call will give a process a single task. apply_async is non-blocking: the whole list starts running.
apply_async returns a result object with .get(timeout=n), .ready(), etc.
"""
# multiple_results = [pool.apply_async(download_images_partial, (catalog, )) for i in range(len(catalog))]
# print(multiple_results)
# print(multiple_results[0])
# tqdm([res.get() for res in multiple_results])

"""
map_async will distribute ALL tasks to workers, and return a single result object
"""
# multiple_results = pool.map_async(download_images_partial, catalog, chunksize=1)
# previous_num_left = multiple_results._number_left
# wait_time = 10
# while not multiple_results.ready():
#     num_left = multiple_results._number_left
#     print("Images left: {}, Rate: {}".format(num_left, (previous_num_left - num_left) / wait_time))
#     previous_num_left = num_left
#     time.sleep(wait_time)

# pool.map_async(download_images_partial, catalog)
# pbar.close()

# pool.close()
# pool.join()