import lookup
from switchbotpy import Scanner


def scan_for_bots(LOG):
    bots = []
    scanner = Scanner()

    addresses = scanner.scan(known_dict=None)
    LOG.debug("addresses: %s", str(addresses))

    for address in addresses:
        bot = lookup.find_device_by_mac(mac=address)
        if bot is None: # new bot
            LOG.debug("insert new bot: %s", address)
            bot_id = lookup.insert_device(mac=address)
            bot = lookup.find_device_by_id(bot_id)

        bots.append(bot)

    return bots


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)
    bots = scan_for_bots(LOG)
    LOG.debug("bots: %s", str(bots))