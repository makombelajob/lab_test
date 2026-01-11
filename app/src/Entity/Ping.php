<?php

namespace App\Entity;

use App\Repository\PingRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PingRepository::class)]
class Ping
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $hostname = null;

    #[ORM\Column(length: 18, nullable: true)]
    private ?string $ipAddress = null;

    #[ORM\Column(nullable: true)]
    private ?bool $status = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $scanAt = null;

    #[ORM\ManyToOne(inversedBy: 'ping')]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $user = null;

    /**
     * @var Collection<int, Reconn>
     */
    #[ORM\OneToMany(targetEntity: Reconn::class, mappedBy: 'ping')]
    private Collection $reconn;

    /**
     * @var Collection<int, Scanner>
     */
    #[ORM\OneToMany(targetEntity: Scanner::class, mappedBy: 'ping')]
    private Collection $scanner;

    /**
     * @var Collection<int, Exploit>
     */
    #[ORM\OneToMany(targetEntity: Exploit::class, mappedBy: 'ping')]
    private Collection $exploit;

    public function __construct()
    {
        $this->reconn = new ArrayCollection();
        $this->scanner = new ArrayCollection();
        $this->exploit = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getHostname(): ?string
    {
        return $this->hostname;
    }

    public function setHostname(?string $hostname): static
    {
        $this->hostname = $hostname;

        return $this;
    }

    public function getIpAddress(): ?string
    {
        return $this->ipAddress;
    }

    public function setIpAddress(?string $ipAddress): static
    {
        $this->ipAddress = $ipAddress;

        return $this;
    }

    public function isStatus(): ?bool
    {
        return $this->status;
    }

    public function setStatus(?bool $status): static
    {
        $this->status = $status;

        return $this;
    }

    public function getScanAt(): ?\DateTimeImmutable
    {
        return $this->scanAt;
    }

    public function setScanAt(\DateTimeImmutable $scanAt): static
    {
        $this->scanAt = $scanAt;

        return $this;
    }

    public function getUser(): ?User
    {
        return $this->user;
    }

    public function setUser(?User $user): static
    {
        $this->user = $user;

        return $this;
    }

    /**
     * @return Collection<int, Reconn>
     */
    public function getReconn(): Collection
    {
        return $this->reconn;
    }

    public function addReconn(Reconn $reconn): static
    {
        if (!$this->reconn->contains($reconn)) {
            $this->reconn->add($reconn);
            $reconn->setPing($this);
        }

        return $this;
    }

    public function removeReconn(Reconn $reconn): static
    {
        if ($this->reconn->removeElement($reconn)) {
            // set the owning side to null (unless already changed)
            if ($reconn->getPing() === $this) {
                $reconn->setPing(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Scanner>
     */
    public function getScanner(): Collection
    {
        return $this->scanner;
    }

    public function addScanner(Scanner $scanner): static
    {
        if (!$this->scanner->contains($scanner)) {
            $this->scanner->add($scanner);
            $scanner->setPing($this);
        }

        return $this;
    }

    public function removeScanner(Scanner $scanner): static
    {
        if ($this->scanner->removeElement($scanner)) {
            // set the owning side to null (unless already changed)
            if ($scanner->getPing() === $this) {
                $scanner->setPing(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Exploit>
     */
    public function getExploit(): Collection
    {
        return $this->exploit;
    }

    public function addExploit(Exploit $exploit): static
    {
        if (!$this->exploit->contains($exploit)) {
            $this->exploit->add($exploit);
            $exploit->setPing($this);
        }

        return $this;
    }

    public function removeExploit(Exploit $exploit): static
    {
        if ($this->exploit->removeElement($exploit)) {
            // set the owning side to null (unless already changed)
            if ($exploit->getPing() === $this) {
                $exploit->setPing(null);
            }
        }

        return $this;
    }
}
