class Settings:
    '''
    Testing set to true when the pytest is running to bypass 
    middleware roll based access checking using original db.
    '''
    TESTING: bool = False

settings = Settings()