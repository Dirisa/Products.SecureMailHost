from Interface import Interface, Attribute

class IMail(Interface):
    """A mail object which knows how to send itself
    
    The mail object is initialized with the following arguments:
    
    mfrom     - mail from tag (only for SMTP server) (string)
    mto       - mail to tag (only for SMTP server)  (string)
    message   - message (email.Message.Message based object)
    smtp_host - SMTP server address (string)
    smtp_port - SMTP server port (string/int)
    **kwargs  - additional keywords:
        o userid   - user name for ESMTP login (string)
        o password - password for ESMTP login (string)
        o forcetls - flag to enforce TLS encryption. Sending will fail if the
                     mailserver doesn't support TLS
    """
   
    def setId(id):
        """Set the unique id of the mail
        
        The unique id is generated using the host name, a time stamp and a
        random value by default. It's used as the key for the mail in the queue.
        
        Type: string
        """

    def getId():
        """Get unique id
        
        The id can be used to identify the mail.
        
        Type: string
        """
        return self.id
    
    def incError():
        """Increase the error counter
        
        Each mail has its own error counter which should be increased inside the
        sender queue when the mail cannot be send.
        """

    def getErrors():
        """Get the state of the error counter
        """

    def send(debug=False):
        """Send mail to the SMTP server
        
        The mail including header from self.message is send to the SMTP server.
        
        send is trying to use starttls if possible. If 'forcetls' is set to a
        true value and starttls isn't supported by the mailserver an error is
        raised.
        
        If an userid and password is applied then send is using an ESMTP login.
        If the server doesn't support esmtp login with a give userid an error is
        raised.

        Note: The data mfrom and mto is independed from the data inside the 
              message header. Read the RFC about SMTP for more informations.
        """
        
    def __str__():
        """Return message as string including header
        """
    
    def info():
        """Return status informations about the mail
        
        The status information includes From, To, Subject, message size and the
        state of the error counter.
        """

    
class IMailQueue(Interface):
    """A generic and thread safe mail queue
    
    It's working like a dict except you can't use __setitem__
    """

    def queue(mails):
        """Sends one or more emails to the queue
        """
    
    def __setitem__(key, obj):
        """__setitem__ is not supported!
        """
        
    def __getitem__(id):
        """Get a mail by id
        """

    def __delitem__(mail_or_id):
        """Removes an email from the queue

        MUST be called within an acquired lock!
        """

    def sync():
        """syncs the queue
        
        Useful to sync a DB in the filesystem

        MUST be called within an acquired lock!
        """
        pass
    
    def mkMailId():
        """Generates an id
        """
    
    def keys():
        """List all mail ids (queue keys)
        """
            
    def has_key(id):
        """Tests if the id is in the queue
        """

    def __len__():
        """Thread safe len() method
        """

class IDataManager(Interface):
    """Objects that manage transactional storage.

    These object's may manage data for other objects, or they may manage
    non-object storages, such as relational databases.
    
    Copied from Zope3 sources
    """

    def abort_sub(transaction):
        """Discard all subtransaction data.

        See subtransaction.txt

        This is called when top-level transactions are aborted.

        No further subtransactions can be started once abort_sub()
        has been called; this is only used when the transaction is
        being aborted.

        abort_sub also implies the abort of a 2-phase commit.

        This should never fail.
        """

    def commit_sub(transaction):
        """Commit all changes made in subtransactions and begin 2-phase commit

        Data are saved *as if* they are part of the current transaction.
        That is, they will not be persistent unless the current transaction
        is committed.

        This is called when the current top-level transaction is committed.

        No further subtransactions can be started once commit_sub()
        has been called; this is only used when the transaction is
        being committed.

        This call also implied the beginning of 2-phase commit.
        """

    # Two-phase commit protocol.  These methods are called by the
    # ITransaction object associated with the transaction being
    # committed.

    def tpc_begin(transaction, subtransaction=False):
        """Begin commit of a transaction, starting the two-phase commit.

        transaction is the ITransaction instance associated with the
        transaction being committed.

        subtransaction is a Boolean flag indicating whether the
        two-phase commit is being invoked for a subtransaction.

        Important note: Subtransactions are modelled in the sense that
        when you commit a subtransaction, subsequent commits should be
        for subtransactions as well.  That is, there must be a
        commit_sub() call between a tpc_begin() call with the
        subtransaction flag set to true and a tpc_begin() with the
        flag set to false.

        """


    def tpc_abort(transaction):
        """Abort a transaction.

        This is always called after a tpc_begin call.

        transaction is the ITransaction instance associated with the
        transaction being committed.

        This should never fail.
        """

    def tpc_finish(transaction):
        """Indicate confirmation that the transaction is done.

        transaction is the ITransaction instance associated with the
        transaction being committed.

        This should never fail. If this raises an exception, the
        database is not expected to maintain consistency; it's a
        serious error.

        """

    def tpc_vote(transaction):
        """Verify that a data manager can commit the transaction

        This is the last chance for a data manager to vote 'no'.  A
        data manager votes 'no' by raising an exception.

        transaction is the ITransaction instance associated with the
        transaction being committed.
        """

    def commit(object, transaction):
        """CCCommit changes to an object

        Save the object as part of the data to be made persistent if
        the transaction commits.
        """

    def abort(object, transaction):
        """Abort changes to an object

        Only changes made since the last transaction or
        sub-transaction boundary are discarded.

        This method may be called either:

        o Outside of two-phase commit, or

        o In the first phase of two-phase commit

        """

    def sortKey():
        """
        Return a key to use for ordering registered DataManagers

        ZODB uses a global sort order to prevent deadlock when it commits
        transactions involving multiple resource managers.  The resource
        manager must define a sortKey() method that provides a global ordering
        for resource managers.
        """

