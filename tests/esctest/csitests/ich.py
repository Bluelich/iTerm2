from esc import NUL
import esccsi
import escio
from escutil import AssertEQ, GetCursorPosition, GetScreenSize, AssertScreenCharsInRectEqual
from esctypes import Point, Rect

class ICHTests(object):
  def __init__(self, args):
    self._args = args

  def blank(self):
    if self._args.expected_terminal == "xterm":
      return ' '
    else:
      return NUL

  def test_ICH_DefaultParam(self):
    """ Test ICH with default parameter """
    esccsi.CSI_CUP(Point(1, 1))
    AssertEQ(GetCursorPosition().x(), 1)
    escio.Write("abcdefg")
    esccsi.CSI_CUP(Point(2, 1))
    AssertEQ(GetCursorPosition().x(), 2)
    esccsi.CSI_ICH()

    AssertScreenCharsInRectEqual(Rect(1, 1, 8, 1),
                                 [ "a" + self.blank() + "bcdefg" ])

  def test_ICH_ExplicitParam(self):
    """Test ICH with explicit parameter. """
    esccsi.CSI_CUP(Point(1, 1))
    AssertEQ(GetCursorPosition().x(), 1)
    escio.Write("abcdefg")
    esccsi.CSI_CUP(Point(2, 1))
    AssertEQ(GetCursorPosition().x(), 2)
    esccsi.CSI_ICH(2)

    AssertScreenCharsInRectEqual(Rect(1, 1, 9, 1),
                                 [ "a" + self.blank() + self.blank() + "bcdefg"])

  def test_ICH_IsNoOpWhenCursorBeginsOutsideScrollRegion(self):
    """Ensure ICH does nothing when the cursor starts out outside the scroll region."""
    esccsi.CSI_CUP(Point(1, 1))
    s = "abcdefg"
    escio.Write(s)

    # Set margin: from columns 2 to 5
    esccsi.CSI_DECSET(esccsi.DECLRMM)
    esccsi.CSI_DECSLRM(2, 5)

    # Position cursor outside margins
    esccsi.CSI_CUP(Point(1, 1))

    # Insert blanks
    esccsi.CSI_ICH(10)

    # Ensure nothing happened.
    esccsi.CSI_DECRESET(esccsi.DECLRMM)
    AssertScreenCharsInRectEqual(Rect(1, 1, len(s), 1),
                                 [ s ])

  def test_ICH_ScrollOffRightEdge(self):
    """Test ICH behavior when pushing text off the right edge. """
    width = GetScreenSize().width()
    s = "abcdefg"
    startX = width - len(s) + 1
    esccsi.CSI_CUP(Point(startX, 1))
    escio.Write(s)
    esccsi.CSI_CUP(Point(startX + 1, 1))
    esccsi.CSI_ICH()

    AssertScreenCharsInRectEqual(Rect(startX, 1, width, 1),
                                 [ "a" + self.blank() + "bcdef" ])
    # Ensure there is no wrap-around.
    AssertScreenCharsInRectEqual(Rect(1, 2, 1, 2), [ NUL ])

  def test_ICH_ScrollEntirelyOffRightEdge(self):
    """Test ICH behavior when pushing text off the right edge. """
    width = GetScreenSize().width()
    esccsi.CSI_CUP(Point(1, 1))
    escio.Write("x" * width)
    esccsi.CSI_CUP(Point(1, 1))
    esccsi.CSI_ICH(width)

    expectedLine = self.blank() * width

    AssertScreenCharsInRectEqual(Rect(1, 1, width, 1),
                                 [ expectedLine ])
    # Ensure there is no wrap-around.
    AssertScreenCharsInRectEqual(Rect(1, 2, 1, 2), [ NUL ])

  def test_ICH_ScrollOffRightMarginInScrollRegion(self):
    """Test ICH when cursor is within the scroll region."""
    esccsi.CSI_CUP(Point(1, 1))
    s = "abcdefg"
    escio.Write(s)

    # Set margin: from columns 2 to 5
    esccsi.CSI_DECSET(esccsi.DECLRMM)
    esccsi.CSI_DECSLRM(2, 5)

    # Position cursor inside margins
    esccsi.CSI_CUP(Point(3, 1))

    # Insert blank
    esccsi.CSI_ICH()

    # Ensure the 'e' gets dropped.
    esccsi.CSI_DECRESET(esccsi.DECLRMM)
    AssertScreenCharsInRectEqual(Rect(1, 1, len(s), 1),
                                 [ "ab" + self.blank() + "cdfg" ])

