# orbital-agent/contracts/orbital_auction.vy
@external
def bid():
    assert block.timestamp < self.auction_end, "Auction ended"
    assert msg.value > self.highest_bid, "Bid too low"
    
    # Refund previous bidder
    if self.highest_bidder != ZERO_ADDRESS:
        send(self.highest_bidder, self.highest_bid)
    
    self.highest_bidder = msg.sender
    self.highest_bid = msg.value
    log.Bid(msg.sender, msg.value)

@view
@external
def get_highest_bid() -> (address, uint256):
    return (self.highest_bidder, self.highest_bid)
