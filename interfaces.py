from Interface import Interface, Attribute
 
class IMail(Interface):
    """Email
    """
    
class IMailQueue(Interface):
    """
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

