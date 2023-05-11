import ctypes as ct
from . import wrapper
from .structures import kvTimeDomainData

dll = wrapper.dll


class TimeDomainData:
    """
    Attributes:
        sync_groups (`int`): Number of MagiSync groups.
        synced_members (`int`): Number of MagiSynced channels.
        non_sync_cards (`int`): Number of MagiSync interfaces.
        non_synced_members (`int`): Number of non-MagiSynced channels.
    """
    def __init__(self, sync_groups, synced_members, non_sync_cards, non_synced_members):
        self.sync_groups = sync_groups
        self.synced_members = synced_members
        self.non_sync_cards = non_sync_cards
        self.non_synced_members = non_synced_members

    def __str__(self):
        return f'sync_groups: {self.sync_groups}, synced_members: {self.synced_members}, non_sync_cards: {self.non_sync_cards}, non_synced_members: {self.non_synced_members}'


class TimeDomain:
    """
    A time domain is a set of channels with a common time base.

    """
    def __init__(self):
        self._domain = ct.c_void_p(None)
        dll.kvTimeDomainCreate(ct.byref(self._domain))

    def close(self):
        """
        Delete all members of the domain and then delete the domain itself.

        """

        if not self._domain:
            return
        dll.kvTimeDomainDelete(self._domain)

    def reset_time(self):
        """
        Reset the time of all channels in the domain.

        """
        if not self._domain:
            return
        dll.kvTimeDomainResetTime(self._domain)

    def add_channel(self, channel):
        """
        Add a channel to the domain.

        Args:
            channel (`~canlib.canlib.Channel`): Canlib channel

        """
        if not self._domain:
            return
        dll.kvTimeDomainAddHandle(self._domain, channel.handle)

    def remove_channel(self, channel):
        """
        Remove a channel from the domain.

        Args:
            channel (`~canlib.canlib.Channel`): Canlib channel

        """
        if not self._domain:
            return
        dll.kvTimeDomainRemoveHandle(self._domain, channel.handle)

    def get_data(self):
        """
        Get Time Domain data about channels and devices in the time domain.

        Returns:
            `~canlib.canlib.TimeDomainData`

        """
        if not self._domain:
            return
        data = kvTimeDomainData()
        dll.kvTimeDomainGetData(self._domain, ct.byref(data), ct.sizeof(data))

        return TimeDomainData(
            sync_groups=data.nMagiSyncGroups,
            synced_members = data.nMagiSyncedMembers,
            non_sync_cards = data.nNonMagiSyncCards,
            non_synced_members = data.nNonMagiSyncedMembers
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
