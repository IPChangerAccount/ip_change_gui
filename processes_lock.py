import time
import logging
import datetime

from multiprocessing import shared_memory

class ProcessesLock:

    LOCK_USER_START_ID = 0
    LOCK_MAX_USER_ID  = 127

    LOCK_EXPIRE_WAIT_TIME_SEC = 10
    LOCK_RETRY_TIME_SEC = 1

    _lock_name   = None

    _shr_mem_obj = None

    def __init__(self, lock_name) -> None:
        self._lock_name = lock_name
    
    def _create_shared_memory(self, id_to_store):
        
        self._shr_mem_obj = shared_memory.SharedMemory(
            create = True, 
            size   = 1,
            name   = self._lock_name)
    
        buffer = self._shr_mem_obj.buf
        
        buffer[0] = id_to_store
    
        logging.debug('Processes lock object is created. User ID is set to: '
                      + str(id_to_store))

    def create_mutex_with_timeout(self):
        start_time = datetime.datetime.now()
    
        timeout = datetime.timedelta(
                seconds = int(self.LOCK_EXPIRE_WAIT_TIME_SEC))
    
        current_mutex_user_id = self.LOCK_USER_START_ID
        this_script_user_id   = self.LOCK_USER_START_ID
    
        while datetime.datetime.now() - start_time < timeout:
            try:
                self._create_shared_memory(this_script_user_id)
                break
    
            except FileExistsError:
    
                existing_shar_mem_mutex = shared_memory.SharedMemory(
                    name = self._lock_name)
    
                fetched_current_user_id = existing_shar_mem_mutex.buf[0]
    
                existing_shar_mem_mutex.close()  
    
                if fetched_current_user_id != current_mutex_user_id:
                    # New user hijacked the mutex. Refresh usage timeout
                    start_time = datetime.datetime.now()
                    current_mutex_user_id = fetched_current_user_id
    
                # Trying to reserve next user ID, so other waiting users 
                # will understand that mutex user changed when this script 
                # instance will posses it. 
                this_script_user_id = current_mutex_user_id + 1\
                    if current_mutex_user_id != self.LOCK_MAX_USER_ID\
                    else self.LOCK_USER_START_ID
                
                logging.debug(
                    f'This mutex user ID is set to: {this_script_user_id}') 
    
                logging.debug('Another search instance is currently reading '
                             + 'cookies. Waiting and going to retry in ' 
                             + str(self.LOCK_RETRY_TIME_SEC)
                             + ' second(s)...')
                time.sleep(self.LOCK_RETRY_TIME_SEC)
        else:
            raise TimeoutError 

    def destroy_lock(self):
        logging.debug('Deleting lock.')
        self._shr_mem_obj.close()      
        self._shr_mem_obj.unlink()

    def try_create_one_app_instance_lock(self):
        """Tries to create a lock.

        Returns:
            bool: True if lock was created. 
                  False - otherwise (probably the lock already
                  created by other app.)
        """

        result = False    
        try:
            self._create_shared_memory(0)
            result = True
            
        except FileExistsError as ex:
            logging.critical(f'File exist exception: {ex}')

        except Exception as exep:
            logging.critical(f'Unexpected exception: {exep}')

        return result
    
           